#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require kubectl helm

info "Installing kube-prometheus-stack ${KPS_CHART_VERSION}"
k create namespace monitoring --dry-run=client -o yaml | k apply -f - >/dev/null
helm --kube-context "$CONTEXT" upgrade --install kube-prometheus-stack kube-prometheus-stack \
  --repo https://prometheus-community.github.io/helm-charts \
  --version "$KPS_CHART_VERSION" \
  --namespace monitoring \
  -f "$ROOT/deploy/observability/kube-prometheus-stack-values.yaml" \
  --wait --timeout 10m >/dev/null

info "Enabling Traefik request metrics, alerts and dashboard"
for manifest in traefik-metrics alerts dashboard; do
  k apply -f "$ROOT/deploy/observability/${manifest}.yaml" >/dev/null
done
k -n kube-system rollout status deployment/traefik --timeout=300s >/dev/null

pass "Monitoring installed. Grafana: make grafana"
