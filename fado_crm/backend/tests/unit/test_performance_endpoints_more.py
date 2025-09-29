# -*- coding: utf-8 -*-
# Tests for performance endpoints: stats, indexes, and metrics

import os
import sys

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

# Ensure project root on sys.path for package-style imports
TEST_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import SessionLocal
from backend.performance_endpoints import router as performance_router

# Create minimal app and include the performance router
app = FastAPI()
app.include_router(performance_router)


# Dependency overrides for admin and DB
class DummyAdmin:
    id = 1
    email = "admin@test.local"


def _override_admin():
    return DummyAdmin()


# Provide a DB session from the default SessionLocal
# Note: Using the same SQLite file configured by default


def _override_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply overrides on app
from backend import performance_endpoints as pe

app.dependency_overrides[pe.get_admin_user] = _override_admin
if pe.get_db is not None:
    app.dependency_overrides[pe.get_db] = _override_db

client = TestClient(app)


def test_performance_stats_endpoint():
    r = client.get("/performance/database/stats")
    assert r.status_code == 200
    data = r.json()
    assert "connection_pool" in data
    assert "timestamp" in data


def test_performance_indexes_endpoint():
    r = client.get("/performance/database/indexes")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)


def test_performance_metrics_endpoint():
    r = client.get("/performance/metrics")
    assert r.status_code == 200
    # Should be text/plain even if Prometheus not available
    assert r.headers.get("content-type", "").startswith("text/plain")
