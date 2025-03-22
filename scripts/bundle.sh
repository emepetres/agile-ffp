#!/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname $(readlink -f $0) )" &> /dev/null && pwd )
pushd $SCRIPT_DIR

cd ..
rm -fr dist
rm -f dist.zip
mkdir dist
cp -r src/. dist/
cp requirements.txt dist/
cd dist && zip -r ../dist.zip .

popd
