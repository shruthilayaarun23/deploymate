import subprocess
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

def run_step(name, command):
    print(f"\n-- {name} --")
    result = subprocess.run(
        [sys.executable] + command,
        capture_output=False
    )
    if result.returncode != 0:
        print(f"FAILED: {name}")
        sys.exit(1)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "normal"

    print("=" * 50)
    print(f"  Deploymate Pipeline")
    print(f"  Mode: {mode}")
    print("=" * 50)

    # Start simulator in background
    print(f"\nStarting simulator in {mode} mode...")
    simulator = subprocess.Popen(
        [sys.executable, "simulator/simulator.py", "--mode", mode],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)  # Wait for simulator to start

    try:
        run_step("Validator", ["validator/validator.py"])
        run_step("Orchestrator", ["orchestrator/orchestrator.py"])
        run_step("Reporter", ["reporter/reporter.py"])
    finally:
        simulator.terminate()
        print("\nSimulator stopped.")

    print("\n" + "=" * 50)
    print("  Pipeline complete. Check reporter/failure_report.json")
    print("=" * 50)