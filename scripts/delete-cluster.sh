#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require k3d
k3d cluster delete "$CLUSTER"
