#!/bin/bash

pushd "$(dirname "$0")"

cd ..
gunicorn -w 4 -k uvicorn.workers.UvicornWorker agileffp.app:app --bind 0.0.0.0:8000

popd