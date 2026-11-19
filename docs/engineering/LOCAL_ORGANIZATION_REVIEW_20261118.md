# Local organization review — 2026-11-18

Scope: original checkout at reviewed parent `364d7fd`, before integrating the
context workflow into draft PR #7. No files were moved, deleted or catalogued.
The user explicitly authorized adding this workflow to PR #7.

## Verified inventory and disposition

`git ls-files --others --exclude-standard -z` found 54 untracked files before
this report: one skill, one Cursor plan, 41 `_WORK` files, one repository map,
eight input files, one test and one helper. A private byte-size/SHA-256 inventory
is retained in `_WORK/local-organization-review-20261118/untracked_inventory.json`.
It contains local filenames and is deliberately not published.

| Group | Decision | Reason / follow-up |
|---|---|---|
| Context skill, map, helper and tests; AGENTS/INDEX/ROADMAP edits | Commit | Requested reusable workflow; explicit bounded file list |
| Eight local Flowers input files | Preserve locally; organization still needed | Seven restricted sources plus the pilot brief are unregistered in the input catalog. The local Flowers manifest consumes the existing source directory. Do not move without updating consumers and recording byte hashes; do not redistribute source text. The brief belongs with project documentation if separately cleared and organized. |
| Seventeen `_WORK` helper/message files | Preserve; candidates for later cleanup | Temporary iteration scripts are in the correct scratch area. No evidence they are maintained tooling or needed in the package. Promote only a demonstrated reusable operation with review/tests; do not execute unknown scratch scripts during cleanup. |
| Twenty-four `_WORK/codex_smoke_chronicle` artifacts | Preserve locally | Two JSON and 22 Markdown files are generated run material. Their presence does not justify publishing or overwriting historical evidence. |
| One `.cursor` plan | Preserve locally | Editor-specific planning material, not runtime or canonical roadmap |
| `docs/engineering/README.md` marked modified | No content commit | `git hash-object` equals `git rev-parse HEAD:docs/engineering/README.md`; normalized Git blob is unchanged |

## Governance consequence

The original checkout's input-catalog check fails on the eight existing
unregistered inputs. This workflow does not weaken the checker, silently register
restricted sources, or move them into another location to manufacture a pass.
The PR #7 worktree uses those sources through a local manifest outside its own
tracked corpus tree; validate that worktree independently. Preserve the catalog
failure in local handoffs until a separately reviewed input organization resolves
it. This is a review disposition, not a completed corpus reorganization.

The context rules require maps and dated branch/PR narratives to be checked at
each pre-merge iteration. No merge is authorized by this commit or review.
