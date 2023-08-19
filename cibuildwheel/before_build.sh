#!/bin/bash

PYTHON_VERSION=$(python3 -c "import platform; print('.'.join(list(platform.python_version_tuple())[:-1]))")
PYTHON_PLATFORM=$(python3 -c "from packaging.tags import sys_tags; print(next(sys_tags()).platform.lower().replace(\"-\", \"_\").replace(\".\", \"_\").replace(\" \", \"_\"))")

echo "Python version: $PYTHON_VERSION"
echo "Python platform: $PYTHON_PLATFORM"

curl -sL https://github.com/python-LimeReport/pyside6/releases/download/py${PYTHON_VERSION}-qt${QT_VERSION}/extra-$PYTHON_PLATFORM.tar.gz | tar -h -zx -C /usr/local