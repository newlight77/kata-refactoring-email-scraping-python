#!/bin/bash -e

BASE_DIR=$(dirname $0)
ROOT_DIR="$(cd $BASE_DIR && pwd -P)"
echo "root dir = $ROOT_DIR"

echo "****************************************************************"
echo "executing pycodestyle"
pycodestyle .
echo "executing pycodestyle done"

echo "****************************************************************"
echo "executing pyflakes"
python ${ROOT_DIR}/run-pyflakes.py
echo "executing pyflakes done"

echo "****************************************************************"
echo "executing mccabe"
python ${ROOT_DIR}/run-mccabe.py 7
echo "executing mccabe done"

# echo "****************************************************************"
# echo "executing pylint"
# pylint app --disable=C0114,C0115
# pylint config --disable=C0114,C0115
# pylint domin
# pylint shared/utils
# pylint tools/linter