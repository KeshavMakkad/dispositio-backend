#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require docker k3d helm kubectl git

VALUES="${VALUES:-values-development.yaml}"
IMAGE_REPO="${IMAGE_REPO:-dispositio-backend}"
TAG="${IMAGE_TAG:-$(git -C "$ROOT" rev-parse --short=7 HEAD)}"
if [[ -z "${IMAGE_TAG:-}" && -n "$(git -C "$ROOT" status --porcelain -- src requirements.txt Dockerfile)" ]]; then
  TAG="${TAG}-dirty"
fi

if [[ "${SKIP_BUILD:-0}" != 1 ]]; then
  info "Building ${IMAGE_REPO}:${TAG}"
  docker build -t "${IMAGE_REPO}:${TAG}" \
    --build-arg GIT_SHA="$TAG" \
    --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$ROOT" >/dev/null
  k3d image import "${IMAGE_REPO}:${TAG}" --cluster "$CLUSTER" >/dev/null
fi

info "Releasing postgres"
helm --kube-context "$CONTEXT" upgrade --install postgres "$ROOT/deploy/helm/postgres" \
  -n "$NAMESPACE" --wait --timeout 5m >/dev/null

info "Releasing dispositio ${TAG} with ${VALUES}"
helm --kube-context "$CONTEXT" upgrade --install dispositio "$ROOT/deploy/helm/dispositio" \
  -n "$NAMESPACE" \
  -f "$ROOT/deploy/helm/dispositio/${VALUES}" \
  --set image.repository="$IMAGE_REPO" \
  --set image.tag="$TAG" \
  "$(helm_rollback_flag)" --wait --timeout 5m "$@"

pass "Released ${TAG}. Verify with: scripts/smoke-test.sh"
