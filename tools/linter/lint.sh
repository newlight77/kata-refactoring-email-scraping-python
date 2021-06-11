#!/bin/bash -e

BASE_DIR=$(dirname $0)
ROOT_DIR="$(cd $BASE_DIR && pwd -P)"
echo "root dir = $ROOT_DIR"

echo "****************************************************************"
echo "executing pycodestyle"
pycodestyle .

echo "****************************************************************"
echo "executing pyflakes"
python ${ROOT_DIR}/run-pyflakes.py

echo "****************************************************************"
echo "executing mccabe"
python ${ROOT_DIR}/run-mccabe.py 7

echo "****************************************************************"
echo "executing pylint"
pylint api
pylint config
pylint domin
pylint shared/utils
pylint tools/linter