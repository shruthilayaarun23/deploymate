import pytest
import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from validator.validator import validate, load_golden

MOCK_GOLDEN = {
    "readings": [{"sensor": "temp_1", "value": 72.0, "status": "ok"}] * 5,
    "expected_status": "ok",
    "min_value": 65,
    "max_value": 80
}

def mock_normal_reading(*args, **kwargs):
    return {"sensor": "temp_1", "value": 72.0, "unit": "C", "status": "ok"}

def mock_noisy_reading(*args, **kwargs):
    return {"sensor": "temp_1", "value": 150.0, "unit": "C", "status": "out_of_range"}

def mock_timeout_reading(*args, **kwargs):
    return {"error": "timeout", "status": "failed"}

def test_normal_mode_passes(monkeypatch):
    monkeypatch.setattr("validator.validator.get_live_reading", mock_normal_reading)
    report = validate(MOCK_GOLDEN, None)
    assert report["summary"]["result"] == "PASS"
    assert report["summary"]["passed"] == 5

def test_noisy_mode_fails(monkeypatch):
    monkeypatch.setattr("validator.validator.get_live_reading", mock_noisy_reading)
    report = validate(MOCK_GOLDEN, None)
    assert report["summary"]["result"] == "FAIL"
    assert report["summary"]["failed"] == 5

def test_timeout_fails(monkeypatch):
    monkeypatch.setattr("validator.validator.get_live_reading", mock_timeout_reading)
    report = validate(MOCK_GOLDEN, None)
    assert report["summary"]["result"] == "FAIL"

def test_report_has_required_keys(monkeypatch):
    monkeypatch.setattr("validator.validator.get_live_reading", mock_normal_reading)
    report = validate(MOCK_GOLDEN, None)
    assert "summary" in report
    assert "details" in report
    assert "total" in report["summary"]
    assert "passed" in report["summary"]
    assert "failed" in report["summary"]