#!/usr/bin/env sh
set -e

STATE=${STATE:-DF}
POLYGON=${POLYGON:-APPS}
FOLDER=${FOLDER:-data/$STATE}
TRIES=${TRIES:-25}
DEBUG=${DEBUG:-False}
TIMEOUT=${TIMEOUT:-30}
MAX_RETRIES=${MAX_RETRIES:-5}

python examples/download_state.py \
  --state "$STATE" \
  --polygon "$POLYGON" \
  --folder "$FOLDER" \
  --tries "$TRIES" \
  --debug "$DEBUG" \
  --timeout "$TIMEOUT" \
  --max_retries "$MAX_RETRIES"
