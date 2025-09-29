import pathlib

import pytest

try:
    import yaml  # type: ignore
except Exception:
    pytest.skip(
        "pyyaml not installed; skipping compose monitoring tests",
        allow_module_level=True,
    )

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]


def _parse_env_list(env_list):
    """
    docker-compose 'environment' can be list of KEY=VALUE strings.
    Return set of keys.
    """
    keys = set()
    for item in env_list or []:
        if isinstance(item, str) and "=" in item:
            k = item.split("=", 1)[0].strip()
            if k:
                keys.add(k)
    return keys


def test_compose_alertmanager_and_prometheus() -> None:
    compose_path = REPO_ROOT / "docker-compose.yml"
    assert compose_path.exists(), f"docker-compose.yml not found at {compose_path}"

    with compose_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    services = data.get("services", {}) or {}

    # Alertmanager service assertions
    assert "alertmanager" in services, "Alertmanager service missing in compose"
    am = services["alertmanager"]

    # Command should include --config.expand-env
    cmd = am.get("command", []) or []
    assert isinstance(cmd, list), (
        f"Expected list command for alertmanager, got: {type(cmd)}"
    )
    assert any("--config.expand-env" in c for c in cmd), (
        f"Alertmanager command missing --config.expand-env: {cmd}"
    )

    # Environment placeholders should exist
    env = am.get("environment", []) or []
    env_keys = _parse_env_list(env)
    for key in [
        "ALERT_SLACK_WEBHOOK_URL",
        "ALERT_SLACK_CHANNEL",
        "ALERT_EMAIL_TO",
        "ALERT_EMAIL_FROM",
        "ALERT_SMTP_HOST",
        "ALERT_SMTP_PORT",
        "ALERT_SMTP_USER",
        "ALERT_SMTP_PASSWORD",
    ]:
        assert key in env_keys, (
            f"Missing environment placeholder for alertmanager: {key}"
        )

    # Prometheus service assertions
    assert "prometheus" in services, "Prometheus service missing in compose"
    prom = services["prometheus"]

    # volumes should include rules mount to /etc/prometheus/rules
    vols = prom.get("volumes", []) or []
    assert any("/etc/prometheus/rules" in str(v) for v in vols), (
        f"Prometheus volumes should include rules mount, got: {vols}"
    )

    # depends_on should include alertmanager
    depends = prom.get("depends_on", []) or []
    if isinstance(depends, dict):  # docker-compose v2 can use object syntax
        dep_keys = set(depends.keys())
    else:
        dep_keys = set(depends)
    assert "alertmanager" in dep_keys, (
        f"Prometheus must depend_on alertmanager, got: {dep_keys}"
    )
