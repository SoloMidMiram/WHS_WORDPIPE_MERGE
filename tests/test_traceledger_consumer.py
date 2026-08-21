"""Validate the TraceLedger-style consumer contract (library boundary).

A TraceLedger consumer depends on the stable public API surface and provides an
EventSink adapter. This test exercises that boundary without a full DOCX run,
so it stays dependency-light and cross-platform.
"""

from __future__ import annotations

import logging
from pathlib import Path

import wordpipe
from wordpipe.core.datatypes import PipelineConfig, RunReport
from wordpipe.events import (
    CompositeSink,
    JsonlSink,
    NullSink,
    StdlibLoggerSink,
    make_sink,
)


class ConsumerSink:
    """A TraceLedger-style event sink adapter."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict]] = []

    def emit(self, level: str, event: str, fields: dict) -> None:
        self.events.append((level, event, fields))


def test_stable_public_api_surface_is_importable():
    """The minimum stable interface is exported from the top-level package."""
    assert callable(wordpipe.process_docx_v3)
    assert callable(wordpipe.process_docx_v3_simple)
    assert wordpipe.PipelineConfig is PipelineConfig
    assert wordpipe.RunReport is RunReport


def test_consumer_can_build_pipeline_config():
    cfg = PipelineConfig(
        in_path=Path("in.docx"), out_path=Path("out.docx"), do_flatten=False
    )
    assert cfg.do_flatten is False


def test_consumer_event_sink_receives_events():
    sink = ConsumerSink()
    sink.emit("INFO", "start", {"run_id": "1"})
    assert sink.events == [("INFO", "start", {"run_id": "1"})]


def test_make_sink_builds_expected_sink(tmp_path: Path):
    assert isinstance(make_sink(logger=None, jsonl_path=None), NullSink)
    assert isinstance(
        make_sink(logger=logging.getLogger("consumer"), jsonl_path=None),
        StdlibLoggerSink,
    )
    jsonl = tmp_path / "events.jsonl"
    assert isinstance(make_sink(logger=None, jsonl_path=str(jsonl)), JsonlSink)
    assert isinstance(
        make_sink(logger=logging.getLogger("consumer"), jsonl_path=str(jsonl)),
        CompositeSink,
    )
