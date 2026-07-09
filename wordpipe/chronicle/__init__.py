"""Chronicle pipeline: importable ingest/merge/categorize index logic."""

from wordpipe.chronicle.categorize import (
    DEFAULT_THEMES as DEFAULT_THEMES,
    build_sidecar_json as build_sidecar_json,
    extract_events as extract_events,
    load_themes as load_themes,
    match_themes as match_themes,
    rebuild_tagged_md as rebuild_tagged_md,
)
from wordpipe.chronicle.ingest import (
    DEFAULT_MOJIBAKE_MAP as DEFAULT_MOJIBAKE_MAP,
    clean_mojibake as clean_mojibake,
    extract_preamble as extract_preamble,
    extract_source_name as extract_source_name,
    extract_title as extract_title,
    find_dates as find_dates,
    format_event as format_event,
    generate_normalised_md as generate_normalised_md,
    parse_date_range as parse_date_range,
    split_into_events as split_into_events,
)
from wordpipe.chronicle.merge import (
    collect_input_files as collect_input_files,
    compute_body_hash as compute_body_hash,
    extract_events as extract_merge_events,
    generate_source_coverage as generate_source_coverage,
    merge_files as merge_files,
    parse_date_tuple as parse_date_tuple,
    parse_yaml_frontmatter as parse_yaml_frontmatter,
    write_duplicates_report as write_duplicates_report,
    write_source_coverage as write_source_coverage,
)

# Rename merge's extract_events to avoid clash with categorize's
extract_events_from_md = extract_merge_events

__all__ = [
    # --- Ingest ---
    "DEFAULT_MOJIBAKE_MAP",
    "clean_mojibake",
    "extract_preamble",
    "extract_source_name",
    "extract_title",
    "find_dates",
    "format_event",
    "generate_normalised_md",
    "parse_date_range",
    "split_into_events",
    # --- Categorize ---
    "DEFAULT_THEMES",
    "build_sidecar_json",
    "extract_events",
    "load_themes",
    "match_themes",
    "rebuild_tagged_md",
    # --- Merge ---
    "collect_input_files",
    "compute_body_hash",
    "extract_events_from_md",
    "generate_source_coverage",
    "merge_files",
    "parse_date_tuple",
    "parse_yaml_frontmatter",
    "write_duplicates_report",
    "write_source_coverage",
]
