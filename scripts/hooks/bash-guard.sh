#!/bin/sh
# Fast pre-filter for the PreToolUse Bash guard.
#
# The guard only acts on a few git command shapes. Spawning node for EVERY
# Bash call to discover that most don't match wastes ~35ms each. So gate it
# with shell BUILTINS only, `read` + a `case` glob, which spawn ZERO extra
# processes. A false match just pays node and gets allowed, so correctness
# never depends on the glob being exact.
#
# Claude Code hook payloads are single-line compact JSON, so one `read` gets
# the whole thing (embedded newlines arrive escaped as \n, not real breaks).
DIR=$(dirname "$0")
IFS= read -r input || true
case "$input" in
  *'git add'* | *'git commit'* | *'git reset'* | *'git clean'* | *'git stash'* | *'git checkout'* | *'git push'* | *'git mv'* | *'git rm'*)
    printf '%s' "$input" | node "$DIR/bash-guard.mjs"
    exit $?
    ;;
esac
exit 0
