"""Pipeline coordination (interfaces-only).

This layer composes core logic using injected interfaces. It must not import
concrete adapters or optional dependencies at module import time.
"""

from wordpipe.orchestration.pipeline import OrchestrationDeps, WordPipePipeline

__all__ = ["OrchestrationDeps", "WordPipePipeline"]

