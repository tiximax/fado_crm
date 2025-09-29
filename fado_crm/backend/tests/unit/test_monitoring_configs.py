import pathlib

import pytest

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    pytest.skip("pyyaml not installed; skipping monitoring config tests", allow_module_level=True)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]


def test_prometheus_config():
    """Sanity-check Prometheus config: alertmanager target and rule_files are present."""
    prom_path = REPO_ROOT / "monitoring" / "prometheus" / "prometheus.yml"
    assert prom_path.exists(), f"Prometheus config not found at {prom_path}"

    with prom_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # rule_files should include /etc/prometheus/rules/*.yml
    rule_files = data.get("rule_files", [])
    assert any("/etc/prometheus/rules/" in str(p) for p in (rule_files or [])), (
        f"Expected rule_files to include /etc/prometheus/rules/*.yml, got: {rule_files}"
    )

    # alerting.alertmanagers[0].static_configs[0].targets should include alertmanager:9093
    alerting = data.get("alerting", {})
    ams = alerting.get("alertmanagers", [])
    assert ams and isinstance(ams, list), "alertmanagers config missing"
    sc = ams[0].get("static_configs", []) if isinstance(ams[0], dict) else []
    assert sc and isinstance(sc, list), "static_configs missing for alertmanagers[0]"
    targets = sc[0].get("targets", []) if isinstance(sc[0], dict) else []
    assert any("alertmanager:9093" == t for t in targets), (
        f"Expected alertmanager target 'alertmanager:9093' in targets, got: {targets}"
    )


def test_prometheus_rules_content():
    """Ensure our Prometheus alert rules file contains expected alerts and severities."""
    rules_path = REPO_ROOT / "monitoring" / "prometheus" / "rules" / "fado_alerts.yml"
    assert rules_path.exists(), f"Rules file not found at {rules_path}"

    with rules_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    groups = data.get("groups", []) or []
    assert any(g.get("name") == "fado_crm_alerts" for g in groups), "Missing group 'fado_crm_alerts'"

    # Collect alerts and verify expected ones are present
    expected = {
        "HighErrorRate",
        "HighLatencyP95",
        "CPUHigh",
        "MemoryHigh",
        "ActiveConnectionsHigh",
        "DatabaseConnectionsHigh",
    }
    found = set()
    severities = {}
    for g in groups:
        for rule in g.get("rules", []) or []:
            name = rule.get("alert")
            if name:
                found.add(name)
                labels = rule.get("labels", {}) or {}
                if name in expected:
                    severities[name] = labels.get("severity")

    missing = expected - found
    assert not missing, f"Missing expected alerts: {sorted(missing)}; found={sorted(found)}"

    # Basic severity checks for present alerts
    for name, sev in severities.items():
        assert sev in {"warning", "critical"}, f"Unexpected severity for {name}: {sev}"


def test_alertmanager_config():
    """Sanity-check Alertmanager base config: uses devnull receiver by default."""
    am_path = REPO_ROOT / "monitoring" / "alertmanager" / "alertmanager.yml"
    assert am_path.exists(), f"Alertmanager config not found at {am_path}"

    with am_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    route = data.get("route", {}) or {}
    assert route.get("receiver") == "devnull", f"Expected default receiver 'devnull', got {route.get('receiver')}"

    receivers = data.get("receivers", []) or []
    names = {r.get("name") for r in receivers if isinstance(r, dict)}
    assert "devnull" in names, f"Expected a 'devnull' receiver in receivers, got {names}"
