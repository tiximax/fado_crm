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