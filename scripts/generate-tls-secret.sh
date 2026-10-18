#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require kubectl openssl

TLS_TMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TLS_TMP_DIR"' EXIT

umask 077
openssl req \
  -x509 \
  -nodes \
  -newkey rsa:2048 \
  -sha256 \
  -days 30 \
  -subj "/CN=${INGRESS_HOST}" \
  -addext "subjectAltName=DNS:${INGRESS_HOST}" \
  -keyout "$TLS_TMP_DIR/tls.key" \
  -out "$TLS_TMP_DIR/tls.crt" \
  >/dev/null 2>&1

kn create secret tls dispositio-tls \
  --cert="$TLS_TMP_DIR/tls.crt" \
  --key="$TLS_TMP_DIR/tls.key" \
  --dry-run=client \
  -o yaml | k apply -f - >/dev/null

pass "Created TLS Secret dispositio-tls for ${INGRESS_HOST}; local key files removed"
