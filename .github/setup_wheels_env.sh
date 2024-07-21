#!/bin/bash

BASE_AUDITWHEEL_REPAIR_OPTIONS="$(cat $GITHUB_WORKSPACE/cibuildwheel/exclude_list.txt | sed -e "s/.*/--exclude &/" | xargs)"

LIBS_TO_EXCLUDE=(
    "libshiboken6.abi3.so.$QT_MAJOR_MINOR_VERSION"
    "libpyside6.abi3.so.$QT_MAJOR_MINOR_VERSION"
    "libpyside6qml.abi3.so.$QT_MAJOR_MINOR_VERSION"
)

for lib in "${LIBS_TO_EXCLUDE[@]}"; do
    BASE_AUDITWHEEL_REPAIR_OPTIONS+=" --exclude $lib"
done

AUDITWHEEL_REPAIR_OPTIONS="$BASE_AUDITWHEEL_REPAIR_OPTIONS"

echo "AUDITWHEEL_REPAIR_OPTIONS=$AUDITWHEEL_REPAIR_OPTIONS" >> "$GITHUB_ENV"

sed -i "s/shiboken6==.*/shiboken6==$QT_VERSION\",/" $GITHUB_WORKSPACE/pyproject.toml
sed -i "s/PySide6==.*/PySide6==$QT_VERSION\",/" $GITHUB_WORKSPACE/pyproject.toml
sed -i "s/shiboken6_generator==.*/shiboken6_generator==$QT_VERSION\",/" $GITHUB_WORKSPACE/pyproject.toml