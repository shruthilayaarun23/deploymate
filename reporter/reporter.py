import json
import os
from datetime import datetime, timezone
from metrics import push_metrics
from dotenv import load_dotenv
load_dotenv()

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def generate_report(orchestrator_results, validator_report):
    failed_boards = {
        board: data
        for board, data in orchestrator_results.items()
        if data["status"] == "FAILURE"
    }

    validation_status = validator_report["summary"]["result"]
    validation_failures = [
        r for r in validator_report["details"]
        if not r["passed"]
    ]

    severity = "LOW"
    if failed_boards and validation_status == "FAIL":
        severity = "CRITICAL"
    elif failed_boards or validation_status == "FAIL":
        severity = "HIGH"

    report = {
        "report_id": f"deploymate-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "severity": severity,
        "overall_status": "FAIL" if failed_boards or validation_status == "FAIL" else "PASS",
        "deployment": {
            "total_boards": len(orchestrator_results),
            "successful": sum(1 for d in orchestrator_results.values() if d["status"] == "SUCCESS"),
            "failed": len(failed_boards),
            "failed_boards": failed_boards
        },
        "validation": {
            "result": validation_status,
            "total_checks": validator_report["summary"]["total"],
            "passed": validator_report["summary"]["passed"],
            "failed": validator_report["summary"]["failed"],
            "failures": validation_failures
        },
        "recommended_action": get_recommendation(severity)
    }

    return report

def get_recommendation(severity):
    recommendations = {
        "CRITICAL": "Immediate action required. Deployment and validation both failed. Roll back and investigate logs.",
        "HIGH": "Urgent attention needed. Partial failure detected. Review failed components before proceeding.",
        "LOW": "System healthy. No action required."
    }
    return recommendations[severity]

def save_report(report, path="reporter/failure_report.json"):
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {path}")
    return path

def print_summary(report):
    print("\n-- Deploymate Failure Report ------------------")
    print(f"  Report ID  : {report['report_id']}")
    print(f"  Severity   : {report['severity']}")
    print(f"  Status     : {report['overall_status']}")
    print(f"  Boards     : {report['deployment']['successful']}/{report['deployment']['total_boards']} succeeded")
    print(f"  Validation : {report['validation']['result']}")
    print(f"  Action     : {report['recommended_action']}")
    print("-----------------------------------------------\n")

if __name__ == "__main__":
    orchestrator_results = load_json("orchestrator/results.json")
    validator_report = load_json("validator/report.json")

    report = generate_report(orchestrator_results, validator_report)
    print_summary(report)
    save_report(report)
    push_metrics(report)