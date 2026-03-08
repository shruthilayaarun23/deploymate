import requests
import json
import time

def load_golden(path="validator/golden.json"):
    with open(path, "r") as f:
        return json.load(f)

def get_live_reading(url="http://localhost:5000/reading", timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        return r.json()
    except requests.exceptions.Timeout:
        return {"error": "timeout", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}

def validate(golden, live):
    results = []

    for i, expected in enumerate(golden["readings"]):
        live_reading = get_live_reading()
        time.sleep(0.2)

        passed = True
        reasons = []

        if live_reading.get("status") == "failed":
            passed = False
            reasons.append(f"Request failed: {live_reading.get('error')}")
        else:
            if live_reading["status"] != golden["expected_status"]:
                passed = False
                reasons.append(f"Status mismatch: got {live_reading['status']}, expected {golden['expected_status']}")

            if not (golden["min_value"] <= live_reading["value"] <= golden["max_value"]):
                passed = False
                reasons.append(f"Value out of range: {live_reading['value']} not in [{golden['min_value']}, {golden['max_value']}]")

        results.append({
            "reading_index": i,
            "passed": passed,
            "live": live_reading,
            "reasons": reasons
        })

    total = len(results)
    passed = sum(1 for r in results if r["passed"])

    return {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "result": "PASS" if passed == total else "FAIL"
        },
        "details": results
    }

if __name__ == "__main__":
    golden = load_golden()
    print("Running validation against golden file...")
    report = validate(golden, None)

    print(f"\nResult: {report['summary']['result']}")
    print(f"Passed: {report['summary']['passed']}/{report['summary']['total']}")

    if report['summary']['result'] == "FAIL":
        print("\nFailures:")
        for r in report['details']:
            if not r['passed']:
                print(f"  Reading {r['reading_index']}: {', '.join(r['reasons'])}")

    with open("validator/report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\nReport saved to validator/report.json")