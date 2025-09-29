# fmt: off
import pathlib

import pytest

try:
    import yaml  # type: ignore
except Exception:
    pytest.skip("pyyaml not installed; skipping grafana provisioning tests", allow_module_level=True)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]


def test_prometheus_datasource_defaults():
    ds_path = (
        REPO_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "datasources"
        / "datasources.yml"
    )
    assert ds_path.exists(), f"Grafana datasources file not found at {ds_path}"

    with ds_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    dss = data.get("datasources", []) or []
    assert dss, "No datasources configured"

    prom = None
    for ds in dss:
        if isinstance(ds, dict) and ds.get("type") == "prometheus":
            prom = ds
            break
    assert prom, "Prometheus datasource not found"

    assert prom.get("url") == "http://prometheus:9090", (
        f"Unexpected Prometheus URL: {prom.get('url')}"
    )
    assert prom.get("isDefault") is True, "Prometheus datasource should be default"
# fmt: on
