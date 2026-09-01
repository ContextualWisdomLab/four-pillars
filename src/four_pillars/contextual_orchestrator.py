"""Compatibility exports for the Contextual Orchestrator infrastructure adapter.

The active ``class ContextualOrchestratorClient`` implementation lives under
``four_pillars.infrastructure.orchestration`` so provider-routing infrastructure
cannot drift back into the application namespace.
"""

from .infrastructure.orchestration.contextual_orchestrator import (
    ContextualOrchestratorClient,
    ContextualOrchestratorError,
    ContextualOrchestratorSchemaError,
)

__all__ = [
    "ContextualOrchestratorClient",
    "ContextualOrchestratorError",
    "ContextualOrchestratorSchemaError",
]
