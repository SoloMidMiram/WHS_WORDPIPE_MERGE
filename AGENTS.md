# Repository Agent Evidence Protocol

These rules apply to every planning, review, and implementation task in this
repository, in addition to higher-priority system and user instructions.

1. Before planning, inspect the current code, tests, manifests, relevant context
   documents, and `git status --short`. Do not treat a prompt summary as proof.
2. Classify material claims as **verified now**, **externally reported**,
   **inferred**, or **unverified**, and cite the supporting path, artifact, or
   command. Never forecast a test count and later report it as observed.
3. Before moving files, inventory their consumers and record byte hashes. Before
   an evidence run, prove the proposed run directory does not exist.
4. `git diff` cannot prove that untracked evidence is unchanged. Use a file
   inventory or hashes when preservation matters.
5. If an expected file is absent, report it as absent and request it when needed;
   never synthesize or silently substitute one.
6. Preserve unrelated dirty-worktree changes. Never reset, overwrite historical
   evidence, or mutate repository files while operating in Plan Mode.
7. Corpus inputs must follow `inputs/README.md` and `inputs/catalog.json`. Run
   the root-layout and input-catalog checks after organizational changes.

## Architecture Stability and Refactor Triggers

Use `ARCHITECTURE_AND_MODULES.md` as the canonical domain crosswalk and dependency-rule source. Run `python tools/check_architecture_boundaries.py --root .` after changing production imports.

Broad topic-runner decomposition is conditional, not an active Project Phase 15 deliverable. Reconsider it only when a third adapter exposes concrete coupling or ontology schema evolution makes the current serializer unsafe.

Those are the primary triggers. A repeated cross-module defect, an import-boundary violation that cannot be repaired locally, or a public contract that cannot evolve safely despite characterization tests is only supporting evidence. A repeated-defect trigger requires two dated occurrences recorded in `JOURNAL.md` or the implementation-alignment audit, including affected production paths, why synchronized edits were required, and the tests proving shared responsibility.

When a trigger is met, characterize current behavior, extract at most one pure seam, preserve CLI/import/JSON contracts, validate, and stop to reassess. Do not combine a feature, schema migration, and package/filesystem move in one slice. Ontology entities and frequently observed terms do not automatically become Python modules.

## Context Retrieval and Reusable Work

For repository planning, implementation and pre-merge reviews, use
`.agents/skills/whs-context-loop/SKILL.md`. Start with a compact local snapshot
and `docs/engineering/REPO_MAP.md`; retrieve only the relevant code, tests and
manifest sections before planning. Use literal keyword grep (`git grep`, or
`rg`) to locate references. A search miss is not proof of absence outside its
scope. Expand deliberately; do not load snapshots, corpora or run outputs by default.

Reuse existing deterministic CLIs and checks before writing one-off scripts or
making model/API calls. Summarize tool results as decisions, locators, observed
counts and remaining uncertainty; do not paste entire logs. Do not claim token
or cost savings without measurement. Context compression must retain source
identity, branch/PR ownership, acceptance limits and unresolved failures.

Before each merge-readiness iteration, prepend a dated narrative entry to the
newest-first iteration section of `ROADMAP.md`. Record branch, PR (or explicitly
none/unverified), reviewed head and base, bounded changes, evidence, unresolved
work and next acceptance decision. Refresh `docs/engineering/REPO_MAP.md` when
paths, tools or ownership change; otherwise record that it was checked. Keep
historical entries and their dated results. Recheck the final head/CI after the
documentation commit: an entry describes its reviewed parent, not its own SHA.
This requirement does not authorize merging or changing another PR.
