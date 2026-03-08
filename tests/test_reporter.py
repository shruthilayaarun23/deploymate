import pytest
import sys
import os

sys.path.insert(0, os.path.abspath("."))
from reporter.reporter import generate_report, get_recommendation

MOCK_ORCHESTRATOR_SUCCESS = {
    "board-1": {"status": "SUCCESS", "logs": "Done", "exit_code": 0,
                "start_time": "2026-01-01T00:00:00", "end_time": "2026-01-01T00:00:02"},
    "board-2": {"status": "SUCCESS", "logs": "Done", "exit_code": 0,
                "start_time": "2026-01-01T00:00:00", "end_time": "2026-01-01T00:00:02"},
}

MOCK_ORCHESTRATOR_FAILURE = {
    "board-1": {"status": "FAILURE", "logs": "Error", "exit_code": 1,
                "start_time": "2026-01-01T00:00:00", "end_time": "2026-01-01T00:00:02"},
    "board-2": {"status": "SUCCESS", "logs": "Done", "exit_code": 0,
                "start_time": "2026-01-01T00:00:00", "end_time": "2026-01-01T00:00:02"},
}

MOCK_VALIDATOR_PASS = {
    "summary": {"total": 5, "passed": 5, "failed": 0, "result": "PASS"},
    "details": []
}

MOCK_VALIDATOR_FAIL = {
    "summary": {"total": 5, "passed": 3, "failed": 2, "result": "FAIL"},
    "details": [
        {"reading_index": 1, "passed": False, "live": {}, "reasons": ["Value out of range"]},
        {"reading_index": 3, "passed": False, "live": {}, "reasons": ["Status mismatch"]},
    ]
}

def test_all_pass_is_low_severity():
    report = generate_report(MOCK_ORCHESTRATOR_SUCCESS, MOCK_VALIDATOR_PASS)
    assert report["severity"] == "LOW"
    assert report["overall_status"] == "PASS"

def test_validation_fail_is_high_severity():
    report = generate_report(MOCK_ORCHESTRATOR_SUCCESS, MOCK_VALIDATOR_FAIL)
    assert report["severity"] == "HIGH"
    assert report["overall_status"] == "FAIL"

def test_both_fail_is_critical():
    report = generate_report(MOCK_ORCHESTRATOR_FAILURE, MOCK_VALIDATOR_FAIL)
    assert report["severity"] == "CRITICAL"
    assert report["overall_status"] == "FAIL"

def test_report_has_required_keys():
    report = generate_report(MOCK_ORCHESTRATOR_SUCCESS, MOCK_VALIDATOR_PASS)
    assert "report_id" in report
    assert "severity" in report
    assert "overall_status" in report
    assert "deployment" in report
    assert "validation" in report
    assert "recommended_action" in report

def test_recommendation_text():
    assert "Roll back" in get_recommendation("CRITICAL")
    assert "Urgent" in get_recommendation("HIGH")
    assert "healthy" in get_recommendation("LOW")