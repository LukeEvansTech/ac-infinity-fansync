# AC Infinity Fan Sync

A small Python daemon that polls the AC Infinity cloud API and syncs an intake fan's speed to a percentage (default 85%) of an exhaust fan's speed, creating a slight positive pressure bias. Ships as a Docker image (`ghcr.io/lukeevanstech/ac-infinity-fansync`) configured entirely via environment variables, with Kubernetes/Flux manifests for deployment.

Status: active (last commit 2026-01-23). Note: this folder is a full repo with a GitHub remote (`LukeEvansTech/ac-infinity-fansync`), not local-only WIP.

## Key files

- `src/main.py` — sync loop entry point
- `src/client.py` — AC Infinity cloud API client
- `README.md` — configuration env vars, Docker/Compose/K8s usage
- `ha-automation.md` / `ha-automation.yaml` / `ha-description.md` — Home Assistant automation notes
- `deploy/kubernetes/` — Flux CD / Helm manifests
- `Dockerfile` — builds the runtime image

## Commands

```bash
docker build -t ac-infinity-fansync .
python -m src.main   # requires ACINFINITY_EMAIL, ACINFINITY_PASSWORD, EXHAUST_CONTROLLER, INTAKE_CONTROLLER env vars
```
