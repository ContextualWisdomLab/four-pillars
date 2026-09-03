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


def test_cleanup_never_exposes_the_nim_key_to_dependency_installation() -> None:
    """Remove the inference credential before fallback reinstalls dependencies."""

    proposer, _, _ = workflow_sections()

    assert "env -u NVIDIA_NIM_API_KEY" in proposer
    assert proposer.index("env -u NVIDIA_NIM_API_KEY") < proposer.index(
        "python -m pip install --require-hashes -r requirements/ci.txt",
        proposer.index("Run bounded NVIDIA NIM fallback"),
    )


def test_model_process_uses_an_explicit_environment_allowlist() -> None:
    """Give OpenCode only NIM plus non-secret runtime configuration."""

    proposer, _, _ = workflow_sections()
    fallback = proposer.split("Run bounded NVIDIA NIM fallback", 1)[1]
    clean_exec = fallback.split("opencode run", 1)[0]

    assert "env -i" in clean_exec
    for allowed in (
        'PATH="$PATH"',
        'HOME="$HOME"',
        'NVIDIA_NIM_API_KEY="$NVIDIA_NIM_API_KEY"',
        'OPENCODE_CONFIG="$OPENCODE_CONFIG"',
        'OPENCODE_DISABLE_AUTOUPDATE="$OPENCODE_DISABLE_AUTOUPDATE"',
        'XDG_CONFIG_HOME="$XDG_CONFIG_HOME"',
        'XDG_CACHE_HOME="$XDG_CACHE_HOME"',
    ):
        assert allowed in clean_exec
    for forbidden in (
        "GH_TOKEN=",
        "GITHUB_TOKEN=",
        "REPOSITORY_TOKEN=",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN=",
        "ACTIONS_RUNTIME_TOKEN=",
        "GITHUB_ENV=",
        "GITHUB_OUTPUT=",
    ):
        assert forbidden not in clean_exec


def test_every_verification_gate_runs_inside_an_explicit_safe_environment() -> None:
    """Keep proposed tests away from model, GitHub, OIDC, and Actions credentials."""

    _, verifier, _ = workflow_sections()
    gate = verifier.split("Run every release-quality gate", 1)[1]
    clean_exec = gate.split("python -m pip check", 1)[0]

    assert "env -i" in clean_exec
    for allowed in (
        'PATH="$PATH"',
        'HOME="$HOME"',
        'PYTHONPATH="$PYTHONPATH"',
        'RUNNER_TEMP="$RUNNER_TEMP"',
    ):
        assert allowed in clean_exec
    for forbidden in (
        "NVIDIA_NIM_API_KEY=",
        "GH_TOKEN=",
        "GITHUB_TOKEN=",
        "REPOSITORY_TOKEN=",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN=",
        "ACTIONS_RUNTIME_TOKEN=",
        "GITHUB_ENV=",
        "GITHUB_OUTPUT=",
    ):
        assert forbidden not in clean_exec


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


def test_publication_revalidates_base_and_source_ref_after_branch_creation() -> None:
    """Never create a PR if the exact base or newly-created source ref moved."""

    _, _, publisher = workflow_sections()
    package = publisher.split("Package exactly one pull request in a trusted step", 1)[1]
    pushed = package.index('git push origin "HEAD:refs/heads/${branch}"')
    created = package.index("gh pr create")
    post_push = package[pushed:created]

    assert 'live_base="$(gh api "repos/${GITHUB_REPOSITORY}/git/ref/heads/${DEFAULT_BRANCH}" --jq ".object.sha")"' in post_push
    assert '[ "$live_base" = "$expected_base" ]' in post_push
    assert 'expected_source="$(git rev-parse HEAD)"' in post_push
    assert 'remote_source="$(git ls-remote --heads origin "refs/heads/${branch}" | cut -f1)"' in post_push
    assert '[ "$remote_source" = "$expected_source" ]' in post_push
    assert "base_branch_advanced_after_push" in post_push
    assert "proposal_branch_identity_mismatch" in post_push
