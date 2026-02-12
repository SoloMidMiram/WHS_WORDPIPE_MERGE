# Merge Map: Wordpipe <-> ChatGPT Chronicle

## Canon content (do not auto-edit except via work orders)
- WordHorrorStories/chatgpt-chronicle/book/02_master_current.md
- WordHorrorStories/chatgpt-chronicle/sources/raw/**

## Chronicle tooling (new code lives here)
- wordpipe/chronicle/

## Reuse targets from wordpipe
- wordpipe/ai/logging_tools.py (JSONL event logs)
- cli/ (CLI patterns)
- wordpipe/core/ (datatypes and utilities)

## Merge policy
- Never rewrite evidence bullets
- Chronicle code must not modify sources/raw
- All code changes must be behind a CLI entrypoint
