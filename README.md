# Deploymate

A lightweight deployment orchestration platform that coordinates 
deployments across multiple environments, validates outcomes, and 
automatically surfaces failures through Jira and Datadog.

## Components
- **Simulator** — emits deployment health signals with configurable fault modes
- **Orchestrator** — coordinates concurrent deployments across multiple targets
- **Validator** — compares outcomes against golden files to detect regressions
- **Reporter** — generates structured failure reports and files Jira tickets

