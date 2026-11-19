---
name: whs-context-loop
description: Retrieve bounded WHS repository context and maintain source-linked plans and pre-merge handoffs. Use for WHS planning, implementation iterations, and merge-readiness reviews.
---

# WHS context loop

Work from the active checkout; never infer that another worktree or PR shares
its code. Repository AGENTS.md and explicit user authorization remain controlling.

## Retrieve

1. Run `python tools/repo_context.py snapshot`. Read
   `docs/engineering/REPO_MAP.md` and the newest relevant ROADMAP entry.
2. Pick the affected lane from the map. Run
   `python tools/repo_context.py find "keyword" --scope tools --scope tests`.
   The helper uses literal, case-insensitive Git grep on tracked text, returns
   bounded locators, and excludes corpus/evidence by default. It does not search
   untracked files. Use `rg -n -F` on explicitly selected local files when needed.
3. Read the enclosing function, its callers, focused tests and relevant manifest.
   Expand only for a concrete missing dependency or conflicting evidence. Search
   results route reading; they do not replace contract inspection.

## Decide and execute

Write a short task capsule: goal; branch/PR/head/base; affected contracts;
evidence locators and classification; next action; unresolved acceptance gate.
Prefer existing runner/checker CLI invocations from the map. Do not recreate
their parsing or checks in model prose. Use a model for judgment that cannot be
settled deterministically, such as semantic labels, after narrowing the inputs.
Never substitute keyword counts for manual truth.

Keep large output local under a fresh `_WORK/<purpose>/` directory, or a topic's
ignored output directory for restricted content. Before creating it prove it is
absent. Preserve originals and hashes. Do not publish retrieved corpus text or
source-derived annotations without authorization. Do not treat a synthetic
smoke, internal consumer test, or byte coverage as full product acceptance.

Run focused checks after a meaningful change. Reuse results only when reviewed
head, relevant files, configuration, dependencies and environment still match;
otherwise invalidate the affected evidence. Avoid repeated full suites without
a changed input or unresolved failure. No new external AI service is required.

## Before each merge-readiness iteration

Reconcile worktree dirt, PR head/base/draft status and ownership separately.
Use GitHub tools or `gh` for metadata; use Playwright MCP if live rendered web
inspection is needed, following the user's browser routing rule.

Prepend a narrative ROADMAP entry using this compact form:

`YYYY-MM-DD — subject (branch; PR or none/unverified).` Explain the goal and
bounded change; identify reviewed head/base and evidence paths/commands; state
what is complete, what remains, and the next decision. Label reported history
separately from verified-now facts. Put future targets above history and label
them proposed dates rather than promises. Check the map; update changed routes.

At readiness run the five governance commands in the map, full pytest and
applicable PowerShell integration. Record actual outcomes and hash invariants.
After any commit, verify exact-head CI independently. If offline, say unverified
and retain the known SHA; do not substitute older CI. Keep merge readiness,
real-corpus acceptance and future capabilities as separate verdicts.

For a handoff, return the capsule plus changed paths, verification and unresolved
items. Do not replay full logs or reload every historical document. Improve this
skill from repeated observed work; avoid adding a rule for every incidental error.
