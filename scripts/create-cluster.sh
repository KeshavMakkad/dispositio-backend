#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require docker k3d kubectl
docker info >/dev/null 2>&1 || fail "Docker is not running"

if k3d cluster list --no-headers 2>/dev/null | awk '{print $1}' | grep -qx "$CLUSTER"; then
  info "Cluster $CLUSTER already exists; starting it"
  k3d cluster start "$CLUSTER" >/dev/null 2>&1 || true
else
  info "Creating one-server, three-agent k3d cluster"
  k3d cluster create "$CLUSTER" \
    --servers 1 \
    --agents 3 \
    --port "80:80@loadbalancer" \
    --port "443:443@loadbalancer" \
    --wait
fi

k3d kubeconfig merge "$CLUSTER" --kubeconfig-merge-default >/dev/null
k wait --for=condition=Ready node --all --timeout=180s >/dev/null

agents=("k3d-${CLUSTER}-agent-0" "k3d-${CLUSTER}-agent-1" "k3d-${CLUSTER}-agent-2")
zones=(zone-a zone-b zone-c)
for index in 0 1 2; do
  k label node "${agents[$index]}" \
    node-role=worker \
    topology.kubernetes.io/zone="${zones[$index]}" \
    --overwrite >/dev/null
done
k taint node "k3d-${CLUSTER}-server-0" node-role=control-plane:NoSchedule --overwrite >/dev/null 2>&1 || true

info "Waiting for Traefik and metrics-server"
for deployment in traefik metrics-server; do
  k -n kube-system wait --for=create "deployment/$deployment" --timeout=300s >/dev/null
  k -n kube-system rollout status "deployment/$deployment" --timeout=300s >/dev/null
done

info "Applying namespace and network policies"
k apply -f "$ROOT/deploy/k8s/namespace.yaml" >/dev/null
k apply -f "$ROOT/deploy/k8s/network-policies/" >/dev/null

pass "Cluster $CLUSTER ready"
k get nodes -L node-role,topology.kubernetes.io/zone
