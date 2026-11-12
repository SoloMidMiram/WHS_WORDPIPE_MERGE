import logging
import sys
from html.parser import HTMLParser
from urllib.parse import unquote

import pytest
from markdown_it import MarkdownIt

from pipeline import index as index_cli
from wordpipe.chronicle import index
from wordpipe.chronicle.cli import categorize
from wordpipe.chronicle.merge import merge_files


class NavigationHTML(HTMLParser):
    def __init__(self, markdown):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.feed(MarkdownIt("commonmark").enable("table").render(markdown))

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.append(attributes["id"])
        if tag == "a" and "href" in attributes:
            self.hrefs.append(attributes["href"])


@pytest.fixture
def tagged_chronicle(tmp_path, monkeypatch):
    paths = []
    for i, (title, body) in enumerate([
        ("گزارش API [v2|beta]", "API error one"),
        ("گزارش API [v2|beta]", "API error two"),
        ("رخداد", "API error three"),
        ("گزارش", "API error four"),
    ]):
        source = tmp_path / f"source-{i}.md"
        source.write_text(
            f"---\nsource: source-{i}\n---\n\n## Event: 2026-01-01 - {title}\n\n{body}\n",
            encoding="utf-8",
        )
        paths.append(source)
    merged = tmp_path / "merged.md"
    merged.write_text(merge_files(paths, conflict_mode="keep-both")[0], encoding="utf-8")
    tagged = tmp_path / "tagged Chronicle.md"
    monkeypatch.setattr(sys, "argv", ["categorize", "--input", str(merged), "--output", str(tagged)])
    categorize.main()
    return tagged


def run_index(tagged, appendix, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", [
        "index", "--input", str(tagged), "--output-dir", str(appendix), *args,
    ])
    index_cli.main()


def test_keep_both_survivors_remain_discoverable(tagged_chronicle, tmp_path, monkeypatch):
    appendix = tmp_path / "appendix"
    run_index(tagged_chronicle, appendix, monkeypatch, "--merged", str(tmp_path / "merged.md"))
    output = (appendix / "event_index.md").read_text(encoding="utf-8")
    assert output.count("گزارش API") == 2
    assert "**Total events:** 4" in output


@pytest.mark.parametrize("renderer", ["jinja", "fallback"])
def test_event_links_resolve_to_unique_tagged_targets(tagged_chronicle, tmp_path, monkeypatch, renderer):
    if renderer == "jinja" and not index.HAS_JINJA2:
        pytest.skip("Jinja2 is not installed")
    if renderer == "fallback":
        monkeypatch.setattr(index, "HAS_JINJA2", False)
    appendix = tmp_path / "appendix with spaces"
    run_index(tagged_chronicle, appendix, monkeypatch)
    tagged_text = tagged_chronicle.read_text(encoding="utf-8")
    expected = index.merged_survivor_anchors((tmp_path / "merged.md").read_text(encoding="utf-8"))
    target = NavigationHTML(tagged_text)
    assert target.ids == expected
    for name in ("event_index.md", "theme_index.md"):
        output = (appendix / name).read_text(encoding="utf-8")
        links = NavigationHTML(output).hrefs
        assert len(set(links)) == 4
        if name == "event_index.md":
            assert [link.split("#")[1] for link in links] == expected
        for href in links:
            path, anchor = href.split("#")
            assert "%20" in path
            assert (appendix / unquote(path)).resolve() == tagged_chronicle.resolve()
            assert target.ids.count(anchor) == 1


def test_anchor_identity_ignores_title_and_equivalent_body_whitespace(tagged_chronicle):
    tagged = tagged_chronicle.read_text(encoding="utf-8")
    equivalent = tagged.replace("گزارش API", "New title").replace(
        "API error one", "API   error\none"
    ).replace("\n", "\r\n")
    assert [ev["anchor"] for ev in index.extract_events_from_tagged(equivalent)] == [
        ev["anchor"] for ev in index.extract_events_from_tagged(tagged)
    ]


@pytest.mark.parametrize("projection", ["title", "date_title"])
def test_explicit_title_projection_links_to_first_survivor(
    tagged_chronicle, tmp_path, monkeypatch, caplog, projection,
):
    appendix = tmp_path / "appendix"
    caplog.set_level(logging.INFO)
    run_index(tagged_chronicle, appendix, monkeypatch, "--dedup-method", projection)
    output = (appendix / "event_index.md").read_text(encoding="utf-8")
    anchors = NavigationHTML(tagged_chronicle.read_text(encoding="utf-8")).ids
    assert [link.split("#")[1] for link in NavigationHTML(output).hrefs] == [
        anchors[0], *anchors[2:],
    ]
    assert f"Explicit {projection} projection omitted 1 survivor entries" in caplog.text


def test_unanchored_input_gets_a_separate_navigation_target(tmp_path, monkeypatch):
    tagged = tmp_path / "legacy.md"
    original = "## Event: 2026-01-01 - Legacy\n\n<!-- themes: API -->\n\nAPI error.\n"
    tagged.write_text(original, encoding="utf-8")
    before = tagged.read_bytes()
    appendix = tmp_path / "appendix"
    run_index(tagged, appendix, monkeypatch)
    output = (appendix / "event_index.md").read_text(encoding="utf-8")
    (link,) = NavigationHTML(output).hrefs
    path, anchor = link.split("#")
    assert path == "chronicle_tagged_anchored.md"
    target = (appendix / path).read_text(encoding="utf-8")
    assert NavigationHTML(target).ids == [anchor]
    assert index.extract_events_from_tagged(target)[0]["anchor"] == anchor
    assert tagged.read_bytes() == before


@pytest.mark.parametrize("damage", ["missing_event", "wrong_anchor", "invalid_renderer", "fenced_links"])
def test_index_rejects_invalid_navigation_before_publication(
    tagged_chronicle, tmp_path, monkeypatch, damage,
):
    if damage == "missing_event":
        text = tagged_chronicle.read_text(encoding="utf-8")
        last_event = text.rindex("## Event:")
        text = text[:last_event].removesuffix("<!-- Duplicate date, different content -->\n\n")
        tagged_chronicle.write_text(text, encoding="utf-8")
    elif damage == "wrong_anchor":
        text = tagged_chronicle.read_text(encoding="utf-8")
        tagged_chronicle.write_text(text.replace("API error two", "wrong event"), encoding="utf-8")
    elif damage == "invalid_renderer":
        monkeypatch.setattr(index_cli, "render_template", lambda *args, **kwargs: "# Empty index")
    else:
        render = index_cli.render_template
        monkeypatch.setattr(index_cli, "render_template",
                            lambda *args, **kwargs: "```markdown\n" + render(*args, **kwargs) + "\n```\n")
    appendix = tmp_path / "appendix"
    with pytest.raises(SystemExit) as error:
        run_index(tagged_chronicle, appendix, monkeypatch, "--merged", str(tmp_path / "merged.md"))
    assert error.value.code == 1
    assert not appendix.exists()
