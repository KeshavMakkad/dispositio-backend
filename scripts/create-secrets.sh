#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require kubectl openssl

random() { openssl rand -base64 32 | tr -d '/+=' | cut -c1-32; }

if kn get secret postgres-credentials >/dev/null 2>&1; then
  info "postgres-credentials already exists; keeping it"
  db_password="$(kn get secret postgres-credentials -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d)"
else
  db_password="$(random)"
  kn create secret generic postgres-credentials \
    --from-literal=POSTGRES_USER=dispositio \
    --from-literal=POSTGRES_PASSWORD="$db_password" >/dev/null
  pass "Created postgres-credentials"
fi

if kn get secret dispositio-secrets >/dev/null 2>&1; then
  info "dispositio-secrets already exists; keeping it"
else
  args=(--from-literal=DB_USER=dispositio
        --from-literal=DB_PASSWORD="$db_password"
        --from-literal=JWT_SECRET="$(random)"
        --from-literal=SHEETS_API_KEY="$(random)")
  if [[ -n "${SUPABASE_JWT_SECRET:-}" ]]; then
    args+=(--from-literal=SUPABASE_JWT_SECRET="$SUPABASE_JWT_SECRET")
  fi
  kn create secret generic dispositio-secrets "${args[@]}" >/dev/null
  pass "Created dispositio-secrets"
fi
