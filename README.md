# Dispositio backend


## Submission

| | |
|---|---|
| Student / ID | Keshav Makkad / 23bcs10002 |
| Repository | https://github.com/KeshavMakkad/dispositio-backend |
| Baseline commit | [`a9e509e0d6349253c5b9dd4cf56bc4bc9f99bbcc`](https://github.com/KeshavMakkad/dispositio-backend/commit/a9e509e0d6349253c5b9dd4cf56bc4bc9f99bbcc) |

**At the baseline:** deployment to Render (`render.yaml`), Alembic migrations,
a Makefile, a `/healthz` endpoint, and two pytest files. The Dockerfile was
empty. There was no CI, no Kubernetes, no monitoring and no security scanning.

**This PR adds:**
- a non-root container image tagged with the commit SHA;
- Helm charts for the API and for Postgres (StatefulSet with a PVC);
- a k3d cluster with Traefik ingress and TLS;
- Pod Security `restricted` and default-deny NetworkPolicies;
- HPA and PDB for production;
- Prometheus/Grafana monitoring with alerts;
- GitHub Actions running tests, secret, code, dependency and image scans, and an approval-gated image push;
- upgraded dependencies with known CVEs.

The application code itself is unchanged. See [docs/DECISIONS.md](docs/DECISIONS.md) for the reasoning and the runbook.

## Prerequisites

Docker, [k3d](https://k3d.io), kubectl, Helm 3 or 4, Python 3.12.

```bash
brew install k3d kubectl helm
```

ports 80 and 443 must be free.

## Run

```bash
make up
```

`make up` runs these steps in order:

| Step | What it does |
|---|---|
| `make cluster` | k3d cluster , namespace, network policies |
| `make tls` | self-signed certificate for `dispositio.localhost`|
| `make secrets` | random DB password and JWT secret; Sheets API key and Supabase JWT secret taken from your shell (`export SHEETS_API_KEY=... SUPABASE_JWT_SECRET=...`) |
| `make monitoring` | kube-prometheus-stack, Traefik metrics, alerts, Grafana dashboard |
| `make deploy` | builds the image for the current commit, imports it, `helm upgrade` for Postgres and the API |
| `make smoke` | end-to-end test |

Production settings (2–5 replicas, HPA, PDB, zone spreading):
```bash
make deploy VALUES=values-production.yaml
```

| Access | |
|---|---|
| API | https://dispositio.localhost |
| API docs | https://dispositio.localhost/docs |
| Grafana | `make grafana` → http://localhost:3000, dashboard "Dispositio" |
| Roll back | `make rollback` |
| Tear down | `make cluster-down` |

Local run without Kubernetes: copy `.env.template` to `.env`, fill it in, then `make run`.

## CI/CD

`.github/workflows/ci.yml` runs on every PR and every push to `master`:

1. **test:** ruff, unit tests
2. **security:** gitleaks (full history), bandit, pip-audit
3. **helm:** lint both charts with development and production values
4. **build:** image tagged with the short commit SHA, Trivy scan (blocks on fixable HIGH/CRITICAL)
5. **publish** (`master` only): waits for approval on the `production` environment, then pushes the scanned image to GHCR