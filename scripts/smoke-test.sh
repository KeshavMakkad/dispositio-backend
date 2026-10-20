#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require kubectl curl git

BASE="https://${INGRESS_HOST}"
CA="$(mktemp)"
trap 'rm -f "$CA"' EXIT
kn get secret dispositio-tls -o jsonpath='{.data.tls\.crt}' | base64 -d > "$CA"
CURL=(curl -sS --cacert "$CA" --resolve "${INGRESS_HOST}:443:127.0.0.1")

info "1. Deployed version"
image="$(kn get deployment dispositio -o jsonpath='{.spec.template.spec.containers[0].image}')"
echo "    running image: $image (git HEAD $(git -C "$ROOT" rev-parse --short=7 HEAD))"
kn rollout status deployment/dispositio --timeout=60s >/dev/null || fail "rollout not complete"
pass "rollout complete"

info "2. HTTPS through Traefik with a verified certificate"
code="$("${CURL[@]}" -o /dev/null -w '%{http_code}' "$BASE/healthz")"
[[ "$code" == 200 ]] || fail "/healthz returned $code"
pass "/healthz 200 over verified TLS"

info "3. Authentication is enforced"
code="$("${CURL[@]}" -o /dev/null -w '%{http_code}' "$BASE/api/v1/auth/me")"
[[ "$code" == 401 ]] || fail "/api/v1/auth/me without a cookie returned $code"
pass "unauthenticated request rejected with 401"

info "4. Write through the API and read it back from Postgres"
key="$(kn get secret dispositio-secrets -o jsonpath='{.data.SHEETS_API_KEY}' | base64 -d)"
name="smoke-$(date +%s)"
code="$("${CURL[@]}" -o /dev/null -w '%{http_code}' -X POST "$BASE/api/v1/classroom/sheets/upsert" \
  -H "X-Sheets-Api-Key: $key" -H 'content-type: application/json' \
  -d "{\"classrooms\":[{\"name\":\"$name\",\"classLayout\":[{\"columnName\":\"A\",\"columnCapacity\":5,\"columnSet\":\"1\"},{\"columnName\":\"B\",\"columnCapacity\":5,\"columnSet\":\"2\"}],\"columnsCount\":2,\"maxRows\":5,\"totalCapacity\":10,\"setOneCapacity\":5,\"setTwoCapacity\":5}]}")"
[[ "$code" == 200 ]] || fail "sheets upsert returned $code"
rows="$(kn exec postgres-0 -c postgres -- sh -c "psql -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" -tAc \"select count(*) from classrooms where classroom_name='$name'\"")"
[[ "$rows" == 1 ]] || fail "classroom $name not found in Postgres"
pass "classroom $name stored in Postgres"

pass "Smoke test passed"
