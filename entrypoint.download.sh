#!/usr/bin/env bash
# entrypoint.download.sh
set -e
exec python examples/download_state.py "$@"
