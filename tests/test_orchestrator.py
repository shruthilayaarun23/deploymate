import pytest
import sys
import os

sys.path.insert(0, os.path.abspath("."))
from orchestrator.orchestrator import run_orchestrator, deploy_to_board

def mock_success_deploy(board_name, results):
    from datetime import datetime, timezone
    results[board_name] = {
        "status": "SUCCESS",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": datetime.now(timezone.utc).isoformat(),
        "logs": "Deploying...\nDone",
        "exit_code": 0
    }

def mock_failure_deploy(board_name, results):
    from datetime import datetime, timezone
    results[board_name] = {
        "status": "FAILURE",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": datetime.now(timezone.utc).isoformat(),
        "logs": "Error: deployment failed",
        "exit_code": 1
    }

def test_all_boards_succeed(monkeypatch):
    monkeypatch.setattr("orchestrator.orchestrator.deploy_to_board", mock_success_deploy)
    results = run_orchestrator(["board-1", "board-2", "board-3"])
    assert all(r["status"] == "SUCCESS" for r in results.values())

def test_all_boards_tracked(monkeypatch):
    monkeypatch.setattr("orchestrator.orchestrator.deploy_to_board", mock_success_deploy)
    results = run_orchestrator(["board-1", "board-2", "board-3"])
    assert len(results) == 3
    assert "board-1" in results
    assert "board-2" in results
    assert "board-3" in results

def test_failure_recorded(monkeypatch):
    monkeypatch.setattr("orchestrator.orchestrator.deploy_to_board", mock_failure_deploy)
    results = run_orchestrator(["board-1"])
    assert results["board-1"]["status"] == "FAILURE"
    assert results["board-1"]["exit_code"] == 1

def test_results_have_required_keys(monkeypatch):
    monkeypatch.setattr("orchestrator.orchestrator.deploy_to_board", mock_success_deploy)
    results = run_orchestrator(["board-1"])
    board = results["board-1"]
    assert "status" in board
    assert "start_time" in board
    assert "end_time" in board
    assert "logs" in board
    assert "exit_code" in board