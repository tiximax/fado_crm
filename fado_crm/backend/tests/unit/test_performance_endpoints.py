# -*- coding: utf-8 -*-
# Basic tests for performance endpoints

import os
import sys

from fastapi.testclient import TestClient

# Đảm bảo có thể import gói 'backend' khi chạy pytest từ root hoặc từ backend
TEST_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from backend.performance_endpoints import router as performance_router
from fastapi import FastAPI

# Tạo app tối thiểu chỉ để kiểm tra router /performance
app = FastAPI()
app.include_router(performance_router)


def test_performance_health_endpoint():
    client = TestClient(app)
    resp = client.get("/performance/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_status" in data
    assert "services" in data
    assert "timestamp" in data
