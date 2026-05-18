#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd -- "${SCRIPT_DIR}/.." && pwd)
IMAGE_NAME=${1:-python:3.12-bullseye}

cd "$PROJECT_ROOT"

docker run --rm \
  -v "$PROJECT_ROOT:/app" \
  -w /app \
  "$IMAGE_NAME" \
  python -m pip install --no-cache-dir \
    -r requirements.txt \
    "torch<=2.11.0" \
    "gradio[oauth,mcp]==5.33.0" \
    "uvicorn>=0.14.0" \
    "websockets>=10.4" \
    spaces==0.50.2