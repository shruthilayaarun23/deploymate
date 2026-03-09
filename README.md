# Deploymate

A lightweight deployment orchestration platform that coordinates deployments
across multiple environments, validates outcomes against known-good baselines,
and automatically surfaces failures with full observability through Datadog.


## Architecture
```
simulator/          Signal emitter with configurable fault modes
    simulator.py    Flask app exposing /reading and /health endpoints

validator/          Regression detection against golden baselines
    validator.py    Compares live readings to golden.json
    golden.json     Captured baseline of known-good readings

orchestrator/       Concurrent multi-board deployment coordinator
    orchestrator.py Deploys to N boards in parallel, tracks state

reporter/           Unified failure analysis and observability
    reporter.py     Aggregates results, scores severity, generates report
    metrics.py      Pushes metrics to Datadog

tests/              Unit tests for all components (13 passing)
run.py              End-to-end pipeline runner
```

## How It Works

1. The **simulator** emits sensor readings over HTTP in one of four modes:
   `normal`, `noisy`, `out_of_range`, or `timeout`

2. The **validator** pulls 10 live readings and compares them against
   a golden file captured during a known-good run. Any deviation is
   flagged with the exact reason.

3. The **orchestrator** concurrently deploys to 3 Docker targets,
   tracking each board through `IDLE → IN_PROGRESS → SUCCESS/FAILURE`

4. The **reporter** aggregates validator and orchestrator results,
   scores severity (`LOW / HIGH / CRITICAL`), and pushes 4 metrics
   to Datadog in real time.

## Fault Modes

| Mode         | Behavior                      | Expected Result      |
|--------------|-------------------------------|----------------------|
| normal       | Readings within range         | PASS, LOW severity   |
| noisy        | Readings ±20-40 from baseline | FAIL, HIGH severity  |
| out_of_range | Readings far outside limits   | FAIL, HIGH severity  |
| timeout      | Simulator delays 10s          | FAIL, timeout errors |

## Datadog Dashboard

Live metrics pushed on every pipeline run, visualized in real time.

![Deploymate Datadog Dashboard](assets/dashboard.png)

| Metric                       | Description                   |
|------------------------------|-------------------------------|
| `deploymate.boards.total`    | Total boards targeted per run |
| `deploymate.boards.success`  | Successful deployments        |
| `deploymate.boards.failed`   | Failed deployments            |
| `deploymate.severity.score`  | 0=LOW, 1=HIGH, 2=CRITICAL     |

## Tech Stack

Python, Flask, Docker, Datadog, GitHub Actions, pytest