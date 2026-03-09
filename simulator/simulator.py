from flask import Flask, jsonify
import random
import time
import argparse

app = Flask(__name__)
MODE = "normal"

def get_reading():
    base = 72.0
    if MODE == "normal":
        return round(base + random.uniform(-1, 1), 2)
    elif MODE == "noisy":
        return round(base + random.choice([-1, 1]) * random.uniform(20, 40), 2)
    elif MODE == "out_of_range":
        return round(base + random.uniform(50, 100), 2)
    elif MODE == "timeout":
        time.sleep(10)
        return round(base, 2)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "mode": MODE})

@app.route("/reading")
def reading():
    value = get_reading()
    return jsonify({
        "sensor": "temp_1",
        "value": value,
        "unit": "C",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": MODE,
        "status": "ok" if 65 <= value <= 80 else "out_of_range"
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="normal",
        choices=["normal", "noisy", "out_of_range", "timeout"])
    args = parser.parse_args()
    MODE = args.mode
    print(f"Starting simulator in {MODE} mode...")
    app.run(port=5000)