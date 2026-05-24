# ARCHITECTURE.md

`wordpipe` - Modular Pipeline Architecture

## 1. Architectural Goals
`wordpipe` is designed to support:
- Lightweight package import
- Independent module usage
- Root-level orchestration embedding
- Optional AI and document processing features
- Long-term extensibility

The architecture enforces strict separation between core logic and infrastructure.

## 2. Layered Structure

```text
wordpipe/
|
|-- core/              # Pure pipeline logic (no runtime dependencies)
|-- interfaces/        # Abstract service contracts
|-- adapters/          # Concrete infrastructure implementations
|-- orchestration/     # Pipeline coordination logic
|-- cli/               # Optional CLI entrypoints
|-- plugins/           # Optional capability registration
`-- __init__.py        # Minimal public API surface
```

## 3. Import Boundary Rules
- No optional dependency may be imported at module load time.
- Optional features must use lazy imports.
- `import wordpipe` must succeed with only core dependencies installed.
- Core modules must never depend on adapters.

## 4. Core Layer
Contains:
- Pure transformation logic
- Stateless pipeline components
- No filesystem, network, or AI dependencies

This layer is fully unit-testable without mocks.

## 5. Interfaces Layer
Defines abstract service contracts:
- DocumentReader
- DocumentWriter
- AISummarizer
- Logger
- ConfigProvider

Core and orchestrator depend only on these interfaces.

## 6. Adapters Layer
Contains concrete implementations:
- docx-based readers/writers
- OpenAI-based summarizers
- Filesystem persistence
- Logging implementations

Adapters may depend on external libraries.

Adapters must not be imported by core.

## 7. Orchestration Layer
Coordinates pipeline stages.

Responsibilities:
- Dependency injection
- Execution flow
- Error handling
- Composition of services

Orchestrator must not instantiate adapters directly.
Dependencies are provided externally or via a composition root.

## 8. Plugin System
Plugins register capabilities dynamically.

Supported mechanisms:
- Entry points
- Runtime registry
- Capability-based loading

Plugins must not modify core behavior implicitly.

## 9. Installation Profiles
Optional dependency groups (extras):
- `wordpipe[docx]`
- `wordpipe[ai]`
- `wordpipe[cli]`
- `wordpipe[full]`

Core installation remains dependency-light.

## 10. Architectural Invariants
- Core has zero runtime-heavy dependencies.
- Interfaces isolate infrastructure.
- Adapters are replaceable.
- Import safety is guaranteed.
- Public API remains minimal and stable.

## Footnote
Tehran Time (Asia/Tehran): 2026-02-14 00:00
Shamsi (Jalali): 1404-11-25

