"""Tests for WordPipePipeline orchestration fail-fast behavior."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from wordpipe.core.datatypes import ChangeNote, PipelineConfig, Segment
from wordpipe.interfaces.ai import AISummarizer
from wordpipe.interfaces.documents import DocumentReader, DocumentSegmenter, DocumentStyler, DocumentWriter
from wordpipe.interfaces.transforms import Flattener, TocUpdater
from wordpipe.orchestration.pipeline import OrchestrationDeps, WordPipePipeline


# ----------------------------------------------------------------------------
# Fake implementations (stdlib only, no python-docx)
# ----------------------------------------------------------------------------


class _OkReader(DocumentReader):
    def read(self, path: Path) -> Any:
        return "fake-doc"

    def close(self, doc: Any) -> None:
        pass


class _FailingReader(DocumentReader):
    def read(self, path: Path) -> Any:  # type: ignore[override]
        raise IOError("read failed")

    def close(self, doc: Any) -> None:
        pass


class _OkStyler(DocumentStyler):
    def ensure_styles(self, doc: Any, *, logger: Any = None) -> None:
        pass

    def style_code_blocks(self, doc: Any, *, logger: Any = None) -> None:
        pass


class _FailingStyler(DocumentStyler):
    def ensure_styles(self, doc: Any, *, logger: Any = None) -> None:
        raise IOError("styler failed")

    def style_code_blocks(self, doc: Any, *, logger: Any = None) -> None:
        pass


class _OkWriter(DocumentWriter):
    def write(self, doc: Any, path: Path) -> None:
        pass


class _FailingWriter(DocumentWriter):
    def write(self, doc: Any, path: Path) -> None:  # type: ignore[override]
        raise IOError("write failed")


class _OkSegmenter(DocumentSegmenter):
    def segment(self, path: Path) -> list[Segment]:
        return [Segment(start_p=0, end_p=10, h1_title="Test", hpath="H1: Test > H2: Sub", bk_name="H1_1")]


class _FailingSegmenter(DocumentSegmenter):
    def segment(self, path: Path) -> list[Segment]:  # type: ignore[override]
        raise IOError("segment failed")


class _OkFlattener(Flattener):
    def flatten(
        self, input_docx: Path, output_docx: Path, *, limit_pages: int | None = None
    ) -> list[ChangeNote]:
        return []


class _FailingFlattener(Flattener):
    def flatten(
        self, input_docx: Path, output_docx: Path, *, limit_pages: int | None = None
    ) -> list[ChangeNote]:  # type: ignore[override]
        raise IOError("flatten failed")


class _OkTocUpdater(TocUpdater):
    def update(self, path: Path) -> None:
        pass


class _FailingTocUpdater(TocUpdater):
    def update(self, path: Path) -> None:  # type: ignore[override]
        raise IOError("toc failed")


# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def cfg() -> PipelineConfig:
    return PipelineConfig(in_path=Path("in.docx"), out_path=Path("out.docx"))


def _make_pipeline(
    *,
    reader: DocumentReader | None = None,
    writer: DocumentWriter | None = None,
    styler: DocumentStyler | None = None,
    segmenter: DocumentSegmenter | None = None,
    flattener: Flattener | None = None,
    toc_updater: TocUpdater | None = None,
) -> WordPipePipeline:
    deps = OrchestrationDeps(
        reader=reader or _OkReader(),
        writer=writer or _OkWriter(),
        styler=styler or _OkStyler(),
        segmenter=segmenter or _OkSegmenter(),
        flattener=flattener,
        toc_updater=toc_updater,
    )
    return WordPipePipeline(deps)


# ----------------------------------------------------------------------------
# Happy path
# ----------------------------------------------------------------------------


class TestHappyPath:
    def test_all_steps_succeed(self, cfg: PipelineConfig):
        """Verify a complete pipeline run returns success."""
        p = _make_pipeline(toc_updater=_OkTocUpdater())
        report = p.run(cfg)
        assert report.errors == []
        assert report.out_path == cfg.out_path
        assert len(report.segments) == 1
        assert report.seconds >= 0


# ----------------------------------------------------------------------------
# fail-fast: style failure → no writer.write called
# ----------------------------------------------------------------------------


class TestStyleFailure:
    def test_styler_error_aborts(self, cfg: PipelineConfig):
        """When styler raises, pipeline should abort before segment/finalize."""
        writer = _OkWriter()
        p = _make_pipeline(styler=_FailingStyler(), writer=writer)
        report = p.run(cfg)
        assert len(report.errors) >= 1
        assert "Style step failed" in report.errors[0]
        assert report.out_path == cfg.out_path
        # Segments should be empty since we aborted before segment_step
        assert report.segments == []

    def test_reader_exception_aborts(self, cfg: PipelineConfig):
        """When reader raises, pipeline should abort before segment."""
        p = _make_pipeline(reader=_FailingReader())
        report = p.run(cfg)
        assert len(report.errors) >= 1
        assert "Style step failed" in report.errors[0]
        assert report.out_path == cfg.out_path


# ----------------------------------------------------------------------------
# fail-fast: flatten failure → pipeline continues with cfg.in_path
# ----------------------------------------------------------------------------


class TestFlattenFailure:
    def test_flatten_error_continues(self, cfg: PipelineConfig):
        """Flatten failure should record error but pipeline continues."""
        p = _make_pipeline(flattener=_FailingFlattener())
        report = p.run(cfg)
        assert len(report.errors) >= 1
        assert "flatten" in report.errors[0].lower()
        # Pipeline should have continued through style/segment/finalize
        assert len(report.segments) == 1


# ----------------------------------------------------------------------------
# fail-fast: segment failure → pipeline continues with []
# ----------------------------------------------------------------------------


class TestSegmentFailure:
    def test_segment_error_continues(self, cfg: PipelineConfig):
        """Segment failure should record error and return empty segments."""
        p = _make_pipeline(segmenter=_FailingSegmenter())
        report = p.run(cfg)
        assert len(report.errors) >= 1
        assert "segment" in report.errors[-1].lower() or "segment" in report.errors[0].lower()
        assert report.segments == []


# ----------------------------------------------------------------------------
# fail-fast: toc failure → report has error but valid out_path
# ----------------------------------------------------------------------------


class TestTocFailure:
    def test_toc_error_continues(self, cfg: PipelineConfig):
        """TOC failure should record error but not abort."""
        p = _make_pipeline(toc_updater=_FailingTocUpdater())
        report = p.run(cfg)
        assert len(report.errors) >= 1
        assert "toc" in report.errors[0].lower()
        assert report.out_path == cfg.out_path
