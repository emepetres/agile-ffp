#!/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname $(readlink -f $0) )" &> /dev/null && pwd )
pushd $SCRIPT_DIR
cd ..

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .