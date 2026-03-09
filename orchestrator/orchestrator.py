import docker
import threading
import time
import json
from datetime import datetime, timezone

client = docker.from_env()

BOARDS = ["board-1", "board-2", "board-3"]

def deploy_to_board(board_name, results):
    results[board_name] = {"status": "IN_PROGRESS", "start_time": datetime.now(timezone.utc).isoformat()}
    print(f"[{board_name}] Deploying...")

    try:
        container = client.containers.run(
            "alpine",
            command="sh -c 'echo Deploying... && sleep 2 && echo Done'",
            name=board_name,
            remove=True,
            detach=True
        )

        exit_code = container.wait()["StatusCode"]
        try:
          logs = container.logs().decode("utf-8").strip()
        except Exception:
          logs = "logs unavailable"

        if exit_code == 0:
            results[board_name] = {
                "status": "SUCCESS",
                "start_time": results[board_name]["start_time"],
                "end_time": datetime.now(timezone.utc).isoformat(),
                "logs": logs,
                "exit_code": exit_code
            }
            print(f"[{board_name}] SUCCESS")
        else:
            results[board_name] = {
                "status": "FAILURE",
                "start_time": results[board_name]["start_time"],
                "end_time": datetime.now(timezone.utc).isoformat(),
                "logs": logs,
                "exit_code": exit_code
            }
            print(f"[{board_name}] FAILURE")

    except Exception as e:
        results[board_name] = {
            "status": "FAILURE",
            "start_time": results[board_name]["start_time"],
            "end_time": datetime.now(timezone.utc).isoformat(),
            "logs": str(e),
            "exit_code": -1
        }
        print(f"[{board_name}] FAILURE -- {e}")

def run_orchestrator(boards=BOARDS):
    print(f"\nStarting deployment across {len(boards)} boards...\n")
    results = {board: {"status": "IDLE"} for board in boards}

    threads = []
    for board in boards:
        t = threading.Thread(target=deploy_to_board, args=(board, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n-- Deployment Summary ------------------")
    for board, result in results.items():
        status = result["status"]
        print(f"  {board}: {status}")
    print("----------------------------------------\n")

    with open("orchestrator/results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to orchestrator/results.json")

    return results

if __name__ == "__main__":
    run_orchestrator()