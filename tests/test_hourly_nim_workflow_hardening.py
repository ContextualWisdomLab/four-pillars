"""Require fail-closed credential and publication handling in the NIM loop."""

from pathlib import Path

WORKFLOW = Path(".github/workflows/hourly-nim-product-development.yml")


def workflow_sections() -> tuple[str, str, str]:
    """Return proposal, verifier, and publisher workflow sections."""

    text = WORKFLOW.read_text(encoding="utf-8")
    proposer = text.split("propose_product_increment:", 1)[1].split(
        "package_product_increment:", 1
    )[0]
    verifier = text.split("package_product_increment:", 1)[1].split(
        "publish_product_increment:", 1
    )[0]
    publisher = text.split("publish_product_increment:", 1)[1]
    return proposer, verifier, publisher


def test_gateway_sidecar_isolates_provider_credentials_from_the_agent() -> None:
    """Scope every provider secret to the gateway step, never the agent step."""

    proposer, _, _ = workflow_sections()

    gateway_step = proposer.split(
        "Start the contextual-orchestrator gateway (orchestrator/free)", 1
    )[1].split("Configure OpenCode for the contextual-orchestrator gateway", 1)[0]
    agent_step = proposer.split("Run the hourly product-development agent", 1)[1]

    for provider_secret in (
        "BYTEZ_API_KEY",
        "NVIDIA_NIM_API_KEY",
        "NVIDIA_NIM_API_KEY_SUB",
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
    ):
        assert f"secrets.{provider_secret}" in gateway_step
        assert provider_secret not in agent_step

    assert proposer.index("Vendor the contextual-orchestrator gateway") < proposer.index(
        "Start the contextual-orchestrator gateway (orchestrator/free)"
    )
    assert proposer.index(
        "Start the contextual-orchestrator gateway (orchestrator/free)"
    ) < proposer.index("Run the hourly product-development agent")


def test_every_verification_gate_runs_after_runtime_channels_are_unset() -> None:
    """Keep proposed tests away from Actions tokens and command files."""

    _, verifier, _ = workflow_sections()
    unset_command = "unset GH_TOKEN GITHUB_TOKEN REPOSITORY_TOKEN"

    assert unset_command in verifier
    assert verifier.index(unset_command) < verifier.index("python -m pip check")
    for token in (
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        "ACTIONS_ID_TOKEN_REQUEST_URL",
        "ACTIONS_RUNTIME_TOKEN",
        "ACTIONS_RUNTIME_URL",
        "ACTIONS_RESULTS_URL",
        "ACTIONS_CACHE_URL",
        "GITHUB_ENV",
        "GITHUB_OUTPUT",
        "GITHUB_PATH",
        "GITHUB_STATE",
        "GITHUB_STEP_SUMMARY",
    ):
        assert token in verifier[verifier.index(unset_command) : verifier.index("python -m pip check")]


def test_artifact_identity_and_remote_branch_inventory_fail_closed() -> None:
    """Reject malformed handoff IDs and distinguish branch absence from API failure."""

    _, verifier, publisher = workflow_sections()
    for section in (verifier, publisher):
        assert '[[ "$artifact_id" =~ ^[1-9][0-9]*$ ]]' in section
        assert '[[ "$expected_artifact_digest" =~ ^[0-9a-f]{64}$ ]]' in section
        assert '[[ "$expected_patch" =~ ^[0-9a-f]{64}$ ]]' in section

    for token in (
        "remote_status=$?",
        "proposal_branch_already_exists",
        "proposal_branch_inventory_unavailable",
    ):
        assert token in publisher
    assert "git ls-remote --exit-code --heads origin" in publisher
    assert "&& exit 1 || true" not in publisher
