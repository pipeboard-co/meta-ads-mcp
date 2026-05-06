#!/bin/bash
#
# Pre-commit check: block commits that introduce email addresses.
# This repo is public — keep email addresses out of the source tree.
#
# Existing emails are grandfathered via .email-allowlist (one pattern per line).
# To add a new allowed email, append it to .email-allowlist.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
ALLOWLIST="$REPO_ROOT/.email-allowlist"

EMAIL_RE='[A-Za-z0-9._%+=-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

# Build a grep -v filter from the allowlist (skip blank lines and comments)
FILTER_ARGS=()
if [ -f "$ALLOWLIST" ]; then
    while IFS= read -r pattern || [ -n "$pattern" ]; do
        # Skip comments and blank lines
        [[ "$pattern" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${pattern// /}" ]] && continue
        FILTER_ARGS+=(-e "$pattern")
    done < "$ALLOWLIST"
fi

# Look at only added lines (starting with +) in the staged diff,
# excluding the diff header lines (+++).
matches=$(git diff --cached --diff-filter=ACMR -U0 -- . \
    ':!.email-allowlist' \
    | grep '^+' \
    | grep -v '^+++' \
    | grep -oE "$EMAIL_RE" \
    || true)

# Remove allowlisted addresses
if [ ${#FILTER_ARGS[@]} -gt 0 ]; then
    matches=$(echo "$matches" | grep -vF "${FILTER_ARGS[@]}" || true)
fi

# Drop empty lines
matches=$(echo "$matches" | sed '/^$/d')

if [ -n "$matches" ]; then
    echo ""
    echo "ERROR: Commit blocked — email address(es) found in staged changes:"
    echo ""
    echo "$matches" | sort -u | while read -r addr; do
        echo "  $addr"
    done
    echo ""
    echo "This is a public repository. Do not commit real email addresses."
    echo "If this email is intentional, add it to .email-allowlist and retry."
    echo ""
    exit 1
fi
