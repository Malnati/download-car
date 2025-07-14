#!/usr/bin/env bash
# entrypoint.download.sh

set -e

STATE=${STATE:-DF}
FOLDER=${FOLDER:-data/$STATE}
POLYGON=${POLYGON:-AREA_PROPERTY}
TRIES=${TRIES:-25}
DEBUG=${DEBUG:-False}
TIMEOUT=${TIMEOUT:-30}
MAX_RETRIES=${MAX_RETRIES:-5}
mkdir -p "$FOLDER"

python cli.py \
  --state "$STATE" \
  --polygon "$POLYGON" \
  --folder "$FOLDER" \
  --tries "$TRIES" \
  --debug "$DEBUG" \
  --timeout "$TIMEOUT" \
  --max_retries "$MAX_RETRIES"



