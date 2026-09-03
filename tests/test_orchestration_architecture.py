"""Lock the DDD model-orchestration boundary against provider-specific regressions."""

from __future__ import annotations

from pathlib import Path

from four_pillars.infrastructure.orchestration.contextual_orchestrator import (
    ContextualOrchestratorClient as InfrastructureClient,
)
from four_pillars.contextual_orchestrator import (
    ContextualOrchestratorClient as CompatibilityClient,
)

ROOT = Path(__file__).parents[1]
SETTINGS = ROOT / "src/four_pillars/settings.py"
ADAPTERS = ROOT / "src/four_pillars/adapters.py"
ENV_EXAMPLE = ROOT / ".env.example"
RETIRED_NIM_MODULE = ROOT / "src/four_pillars/nim.py"
ORCHESTRATION_ROOT = ROOT / "src/four_pillars/infrastructure/orchestration"


def test_provider_specific_runtime_module_stays_retired() -> None:
    """Prevent the old provider-specific transport namespace from reappearing."""
    assert not RETIRED_NIM_MODULE.exists()
    assert (ORCHESTRATION_ROOT / "openai_compatible.py").is_file()
    assert (ORCHESTRATION_ROOT / "contextual_orchestrator.py").is_file()


def test_product_composition_contains_no_provider_native_runtime_contract() -> None:
    """Keep provider credentials and backend selection outside Four Pillars settings."""
    settings = SETTINGS.read_text(encoding="utf-8")
    adapters = ADAPTERS.read_text(encoding="utf-8")
    env_example = ENV_EXAMPLE.read_text(encoding="utf-8")

    for forbidden in (
        "nvidia_nim_api_key",
        "nim_base_url",
        "nim_model",
        "nim_eval_model",
        "NVIDIA_NIM_API_KEY",
    ):
        assert forbidden not in settings
        assert forbidden not in env_example
    assert "NimReportInterpreter" not in adapters
    assert 'Literal["orchestrator/free"]' in settings


def test_compatibility_import_delegates_to_infrastructure_acl() -> None:
    """Keep the historical import path as a re-export rather than a second client."""
    assert CompatibilityClient is InfrastructureClient
