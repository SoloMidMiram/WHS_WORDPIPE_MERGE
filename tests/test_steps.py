"""Unit tests for individual WordPipe step modules.

Uses fake/dummy implementations — no python-docx, no real filesystem I/O.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pytest

from wordpipe.core.datatypes import ChangeNote, PipelineConfig, Segment
from wordpipe.events import EventSink, NullSink
from wordpipe.interfaces.documents import DocumentReader, DocumentSegmenter, DocumentStyler, DocumentWriter
from wordpipe.interfaces.transforms import Flattener, TocUpdater
from wordpipe.steps import (
    FinalizeResult,
    FlattenResult,
    SegmentResult,
    StyleResult,
    TocResult,
    finalize_step,
    flatten_step,
    segment_step,
    style_step,
    toc_step,
)


# ----------------------------------------------------------------------------
# Fake implementations
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


@pytest.fixture
def working() -> Path:
    return Path("work.docx")


@pytest.fixture
def sink() -> EventSink:
    return NullSink()


# ----------------------------------------------------------------------------
# flatten_step
# ----------------------------------------------------------------------------


class TestFlattenStep:
    def test_skip_when_disabled(self, cfg: PipelineConfig, sink: EventSink):
        """When do_flatten=False, step should skip."""
        cfg = PipelineConfig(in_path=cfg.in_path, out_path=cfg.out_path, do_flatten=False)
        result: FlattenResult = flatten_step(cfg, _OkFlattener(), sink)
        assert result.skipped is True
        assert result.error is None

    def test_skip_when_no_flattener(self, cfg: PipelineConfig, sink: EventSink):
        """When flattener is None, step should skip."""
        result: FlattenResult = flatten_step(cfg, None, sink)
        assert result.skipped is True
        assert result.error is None

    def test_success_changes_working_path(self, cfg: PipelineConfig, sink: EventSink):
        """Successful flatten should return a different working path."""
        result: FlattenResult = flatten_step(cfg, _OkFlattener(), sink)
        assert result.error is None
        assert result.skipped is False
        assert result.working_path != cfg.in_path

    def test_failure_returns_original_path(self, cfg: PipelineConfig, sink: EventSink):
        """Flatten failure should return original path + error."""
        result: FlattenResult = flatten_step(cfg, _FailingFlattener(), sink)
        assert result.error is not None
        assert "flatten" in result.error.lower()
        assert result.working_path == cfg.in_path


# ----------------------------------------------------------------------------
# style_step
# ----------------------------------------------------------------------------


class TestStyleStep:
    def test_success_returns_doc(self, cfg: PipelineConfig, sink: EventSink):
        """Successful style step should return a doc."""
        result: StyleResult = style_step(cfg, Path("in.docx"), _OkReader(), _OkStyler(), sink)
        assert result.error is None
        assert result.doc is not None
        assert result.doc == "fake-doc"

    def test_reader_exception_captured(self, cfg: PipelineConfig, sink: EventSink):
        """When reader raises, step should return doc=None + error."""
        result: StyleResult = style_step(cfg, Path("in.docx"), _FailingReader(), _OkStyler(), sink)
        assert result.error is not None
        assert "Style step failed" in result.error
        assert result.doc is None

    def test_styler_exception_captured(self, cfg: PipelineConfig, sink: EventSink):
        """When styler raises, step should return doc=None + error."""
        result: StyleResult = style_step(cfg, Path("in.docx"), _OkReader(), _FailingStyler(), sink)
        assert result.error is not None
        assert "Style step failed" in result.error
        # Step catches all exceptions and discards the doc
        assert result.doc is None


# ----------------------------------------------------------------------------
# segment_step
# ----------------------------------------------------------------------------


class TestSegmentStep:
    def test_success_returns_segments(self, cfg: PipelineConfig, sink: EventSink):
        """Successful segment step should return segments."""
        result: SegmentResult = segment_step(cfg, Path("in.docx"), _OkSegmenter(), sink)
        assert result.error is None
        assert len(result.segments) == 1

    def test_failure_returns_empty(self, cfg: PipelineConfig, sink: EventSink):
        """Segment failure should return empty list + error."""
        result: SegmentResult = segment_step(cfg, Path("in.docx"), _FailingSegmenter(), sink)
        assert result.error is not None
        assert "Segment step failed" in result.error
        assert result.segments == []


# ----------------------------------------------------------------------------
# finalize_step
# ----------------------------------------------------------------------------


class TestFinalizeStep:
    def test_success_writes_via_writer(self, cfg: PipelineConfig, sink: EventSink, working: Path):
        """Successful finalize should write via writer."""
        result: FinalizeResult = finalize_step(cfg, "fake-doc", working, _OkWriter(), sink)
        assert result.error is None
        assert result.out_path == cfg.out_path

    def test_doc_none_produces_error(self, cfg: PipelineConfig, sink: EventSink, working: Path):
        """When doc is None, writer.write should still be attempted and fail."""
        result: FinalizeResult = finalize_step(cfg, None, working, _FailingWriter(), sink)
        assert result.error is not None
        assert result.out_path == cfg.out_path


# ----------------------------------------------------------------------------
# toc_step
# ----------------------------------------------------------------------------


class TestTocStep:
    def test_skip_when_no_updater(self, cfg: PipelineConfig, sink: EventSink):
        """When toc_updater is None, step should skip."""
        result: TocResult = toc_step(cfg, Path("out.docx"), None, sink)
        assert result.updated is False
        assert result.error is None

    def test_success_when_updater_present(self, cfg: PipelineConfig, sink: EventSink):
        """When updater is present, step should succeed."""
        result: TocResult = toc_step(cfg, Path("out.docx"), _OkTocUpdater(), sink)
        assert result.updated is True
        assert result.error is None

    def test_failure_records_error(self, cfg: PipelineConfig, sink: EventSink):
        """When updater raises, step should record error without raising."""
        result: TocResult = toc_step(cfg, Path("out.docx"), _FailingTocUpdater(), sink)
        assert result.updated is False
        assert result.error is not None
        assert "TOC update failed" in result.error
