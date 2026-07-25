"""Unit tests for segmenter heading path computation.

Uses fake paragraph objects — no real DOCX file required.
"""

from __future__ import annotations

from typing import Any, List

from wordpipe.adapters.docx.segmenter import (
    _build_hpath_from_state,
    _precompute_heading_states,
)


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


class _FakePara:
    """Minimal fake paragraph with style and text."""

    def __init__(self, style_name: str, text: str = ""):
        self.style = _FakeStyle(style_name) if style_name else None
        self._text = text

    def text(self) -> str:  # noqa: D102
        return self._text

    @property
    def text(self):  # noqa: D102
        return self._text


class _FakeStyle:
    def __init__(self, name: str):
        self.name = name


def _make_doc(paras: List[dict]) -> Any:
    """Create a fake doc object from a list of {style, text} dicts."""
    return type("FakeDoc", (), {"paragraphs": [_FakePara(**p) for p in paras]})()


# ----------------------------------------------------------------------------
# _precompute_heading_states
# ----------------------------------------------------------------------------


class TestPrecomputeHeadingStates:
    def test_no_headings(self):
        """Without any headings, all entries get (No H1, None, None, None)."""
        doc = _make_doc([
            {"style_name": "Normal", "text": "Intro"},
            {"style_name": "Normal", "text": "Body"},
        ])
        states = _precompute_heading_states(doc)
        assert len(states) == 2
        for h1, h2, h3, idx in states:
            assert h1 == "(No H1)"
            assert h2 is None
            assert h3 is None
            assert idx is None

    def test_single_h1(self):
        """A single H1 propagates to all following paragraphs."""
        doc = _make_doc([
            {"style_name": "Heading 1", "text": "Chapter 1"},
            {"style_name": "Normal", "text": "Content"},
        ])
        states = _precompute_heading_states(doc)
        assert len(states) == 2
        # Paragraph 0 is the H1 itself
        assert states[0][0] == "Chapter 1"
        assert states[0][3] == 1
        # Paragraph 1 inherits the H1
        assert states[1][0] == "Chapter 1"
        assert states[1][3] == 1
        assert states[1][1] is None
        assert states[1][2] is None

    def test_two_h1(self):
        """A second H1 resets H2/H3 and increments the counter."""
        doc = _make_doc([
            {"style_name": "Heading 1", "text": "Ch1"},
            {"style_name": "Heading 2", "text": "Sub"},
            {"style_name": "Heading 1", "text": "Ch2"},
            {"style_name": "Normal", "text": "More"},
        ])
        states = _precompute_heading_states(doc)
        # Para 0: H1, counter=1
        assert states[0] == ("Ch1", None, None, 1)
        # Para 1: H2 under H1
        assert states[1][:3] == ("Ch1", "Sub", None)
        assert states[1][3] == 1
        # Para 2: new H1, counter=2, H2 cleared
        assert states[2] == ("Ch2", None, None, 2)
        # Para 3: inherits Ch2
        assert states[3] == ("Ch2", None, None, 2)

    def test_h1_with_h2_h3(self):
        """H2 then H3 are captured and reset by new H1."""
        doc = _make_doc([
            {"style_name": "Heading 1", "text": "Ch1"},
            {"style_name": "Heading 2", "text": "Section"},
            {"style_name": "Heading 3", "text": "Subsection"},
            {"style_name": "Normal", "text": "Detail"},
        ])
        states = _precompute_heading_states(doc)
        assert states[0] == ("Ch1", None, None, 1)
        assert states[1] == ("Ch1", "Section", None, 1)
        assert states[2] == ("Ch1", "Section", "Subsection", 1)
        assert states[3] == ("Ch1", "Section", "Subsection", 1)

    def test_h2_only_does_not_set_h1_index(self):
        """H2 without prior H1 leaves h1_index as None."""
        doc = _make_doc([
            {"style_name": "Heading 2", "text": "Orphan"},
        ])
        states = _precompute_heading_states(doc)
        assert states[0] == ("(No H1)", "Orphan", None, None)

    def test_empty_h1_text(self):
        """An H1 with empty text still increments the counter."""
        doc = _make_doc([
            {"style_name": "Heading 1", "text": ""},
        ])
        states = _precompute_heading_states(doc)
        assert states[0][0] == "(No H1)"  # empty text → "(No H1)"
        assert states[0][3] == 1  # counter still incremented

    def test_h2_sibling_transition(self):
        """A second H2 (sibling) replaces the first and clears H3.

        Sequence: H1 → H2-A → H3-A → H2-B → paragraph → H3-B
        """
        doc = _make_doc([
            {"style_name": "Heading 1", "text": "Title"},
            {"style_name": "Heading 2", "text": "First section"},
            {"style_name": "Heading 3", "text": "Subsection under A"},
            {"style_name": "Normal", "text": "paragraph content"},
            {"style_name": "Heading 2", "text": "Second section"},
            {"style_name": "Normal", "text": "paragraph content"},
            {"style_name": "Heading 3", "text": "Subsection under B"},
            {"style_name": "Normal", "text": "paragraph content"},
        ])
        states = _precompute_heading_states(doc)

        # Para 3: H3-A paragraph → H2=First section, H3=Subsection under A
        assert states[3][0] == "Title"
        assert states[3][1] == "First section"
        assert states[3][2] == "Subsection under A"

        # Para 4: H2-B line itself → H2=Second section, H3=None
        assert states[4][1] == "Second section"
        assert states[4][2] is None

        # Para 5: After H2-B → H2=Second section, H3=None
        assert states[5][1] == "Second section"
        assert states[5][2] is None

        # Para 6: H3-B line itself → H2=Second section, H3=Subsection under B
        assert states[6][1] == "Second section"
        assert states[6][2] == "Subsection under B"

        # Para 7: After H3-B → H2=Second section, H3=Subsection under B
        assert states[7][1] == "Second section"
        assert states[7][2] == "Subsection under B"


# ----------------------------------------------------------------------------
# _build_hpath_from_state
# ----------------------------------------------------------------------------


class TestBuildHPathFromState:
    def test_h1_only(self):
        """H1 only maps to 'H1: title' with bk H1_1."""
        h1, hpath, bk = _build_hpath_from_state("Intro", None, None, 1)
        assert h1 == "Intro"
        assert hpath == "H1: Intro"
        assert bk == "H1_1"

    def test_h1_h2(self):
        """H1 + H2 produces joined path."""
        h1, hpath, bk = _build_hpath_from_state("Intro", "Section", None, 1)
        assert hpath == "H1: Intro > H2: Section"
        assert bk == "H1_1"

    def test_h1_h2_h3(self):
        """H1 + H2 + H3 produces three-level path."""
        h1, hpath, bk = _build_hpath_from_state("Intro", "Section", "Detail", 2)
        assert hpath == "H1: Intro > H2: Section > H3: Detail"
        assert bk == "H1_2"

    def test_no_bk_when_no_h1(self):
        """Without H1, bk is None."""
        h1, hpath, bk = _build_hpath_from_state("(No H1)", None, None, None)
        assert hpath == "H1: (No H1)"
        assert bk is None
