#!/bin/bash

PYTHON_PLATFORM=$(python3 -c "from packaging.tags import sys_tags; print(next(sys_tags()).platform.lower().replace(\"-\", \"_\").replace(\".\", \"_\").replace(\" \", \"_\"))")

echo "Python platform: $PYTHON_PLATFORM"

curl -L https://github.com/python-LimeReport/pyside6/releases/download/py${PYTHON_VERSION}-qt${QT_VERSION}/extra-$PYTHON_PLATFORM.tar.gz | tar -h -zx -C /usr/local