#!/bin/sh
# openv.sh — run a command with blogger's 1Password Environment injected.
# Usage: scripts/openv.sh <command> [args...]
#
# - Secrets come from the 1Password Environment below (source of truth).
# - The service-account bootstrap token is read per-invocation from a local
#   0600 file and stripped from the child environment (op run inherits it).
# - The environment ID is an identifier, not a secret.

set -eu

OP_ENV_ID="hzj63tuke6gmarsutvcxemvjqq"
OP_TOKEN_FILE="${OP_TOKEN_FILE:-$HOME/.config/op/tokens/blogger-dev}"
OP_BIN="${OP_BIN:-op-beta}"   # Environments CLI surface requires the beta channel (as of 2.35 stable)

if [ ! -r "$OP_TOKEN_FILE" ]; then
  echo "openv.sh: token file not readable: $OP_TOKEN_FILE" >&2
  exit 78
fi

OP_SERVICE_ACCOUNT_TOKEN=$(cat "$OP_TOKEN_FILE") \
exec "$OP_BIN" run --environment "$OP_ENV_ID" -- \
  sh -c 'unset OP_SERVICE_ACCOUNT_TOKEN; exec "$@"' sh "$@"
