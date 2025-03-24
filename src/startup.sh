#!/bin/bash
set -e

pushd "$(dirname "$0")"

gunicorn -w 2 -k uvicorn.workers.UvicornWorker agileffp.app:app --bind 0.0.0.0:8000

popd
