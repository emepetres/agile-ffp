#!/bin/bash

pushd "$(dirname "$0")"

cd ..
python -m agileffp.app

popd