#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER="${DISPOSITIO_CLUSTER:-dispositio}"
CONTEXT="k3d-${CLUSTER}"
NAMESPACE="${DISPOSITIO_NAMESPACE:-dispositio}"
INGRESS_HOST="${DISPOSITIO_HOST:-dispositio.localhost}"
KPS_CHART_VERSION=91.8.2

pass() { printf '[PASS] %s\n' "$*"; }
info() { printf '[INFO] %s\n' "$*"; }
fail() { printf '[FAIL] %s\n' "$*" >&2; exit 1; }
k() { kubectl --context "$CONTEXT" "$@"; }
kn() { kubectl --context "$CONTEXT" -n "$NAMESPACE" "$@"; }

require() {
  for command in "$@"; do
    command -v "$command" >/dev/null || fail "$command is required"
  done
}

helm_rollback_flag() {
  if helm version --short 2>/dev/null | grep -q '^v3'; then echo --atomic; else echo --rollback-on-failure; fi
}
