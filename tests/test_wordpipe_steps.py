from __future__ import annotations

from pathlib import Path

from wordpipe.core.datatypes import PipelineConfig, Segment
from wordpipe.orchestration.pipeline import OrchestrationDeps, WordPipePipeline
from wordpipe.steps import finalize_step, flatten_step, segment_step, style_step, toc_step


class Events:
    def __init__(self):
        self.events = []

    def emit(self, level, event, fields):
        self.events.append((level, event, fields))


class Reader:
    def __init__(self, doc="doc", fail=False):
        self.doc = doc
        self.fail = fail

    def read(self, path: Path):
        if self.fail:
            raise RuntimeError("read boom")
        return self.doc


class Styler:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def ensure_styles(self, doc, *, logger=None):
        self.calls.append("ensure")
        if self.fail:
            raise RuntimeError("style boom")

    def style_code_blocks(self, doc, *, logger=None):
        self.calls.append("code")


class Writer:
    def __init__(self):
        self.writes = []

    def write(self, doc, path: Path):
        self.writes.append((doc, path))


class Segmenter:
    def __init__(self):
        self.calls = 0

    def segment(self, path: Path):
        self.calls += 1
        return [Segment(0, 1, "Title", "H1: Title", "H1_1")]


class Flattener:
    def flatten(self, input_docx: Path, output_docx: Path, *, limit_pages=None):
        output_docx.write_text("work", encoding="utf-8")
        return []


class FailingFlattener:
    def flatten(self, input_docx: Path, output_docx: Path, *, limit_pages=None):
        raise RuntimeError("flatten boom")


class TocUpdater:
    def __init__(self, fail=False):
        self.fail = fail
        self.updated = []

    def update(self, docx_path: Path):
        if self.fail:
            raise RuntimeError("toc boom")
        self.updated.append(docx_path)


def cfg(tmp_path, *, do_flatten=False):
    return PipelineConfig(tmp_path / "in.docx", tmp_path / "out.docx", do_flatten=do_flatten)


def test_flatten_failure_is_recoverable_and_keeps_input_path(tmp_path):
    c = cfg(tmp_path, do_flatten=True)
    result = flatten_step(c, FailingFlattener())
    assert result.working_path == c.in_path
    assert result.error == "Flatten failed: flatten boom"


def test_style_step_returns_doc_on_success(tmp_path):
    result = style_step(cfg(tmp_path), tmp_path / "in.docx", Reader("styled"), Styler())
    assert result.doc == "styled"
    assert result.error is None


def test_segment_step_reports_segments(tmp_path):
    result = segment_step(cfg(tmp_path), tmp_path / "in.docx", Segmenter())
    assert result.segments[0].h1_title == "Title"
    assert result.error is None


def test_finalize_step_writes_and_cleans_intermediate(tmp_path):
    c = cfg(tmp_path)
    working = tmp_path / "out.docx.work.docx"
    working.write_text("work", encoding="utf-8")
    writer = Writer()
    result = finalize_step(c, "doc", working, writer)
    assert writer.writes == [("doc", c.out_path)]
    assert not working.exists()
    assert result.error is None


def test_toc_step_is_optional_and_reports_update_failures(tmp_path):
    c = cfg(tmp_path)
    assert toc_step(c, c.out_path, None).updated is False
    failed = toc_step(c, c.out_path, TocUpdater(fail=True))
    assert failed.error == "TOC update failed: toc boom"


def test_pipeline_style_failure_is_fatal(tmp_path):
    c = cfg(tmp_path, do_flatten=True)
    writer = Writer()
    segmenter = Segmenter()
    sink = Events()
    deps = OrchestrationDeps(
        reader=Reader(fail=True),
        writer=writer,
        styler=Styler(),
        segmenter=segmenter,
        logger=sink,
        flattener=Flattener(),
    )
    report = WordPipePipeline(deps).run(c)

    assert report.errors == ["Style step failed: read boom"]
    assert report.out_path == c.out_path
    assert report.segments == []
    assert writer.writes == []
    assert segmenter.calls == 0
    assert any(event == "fatal_style_failure" for _, event, _ in sink.events)
