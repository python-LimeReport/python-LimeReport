#!/bin/bash

AUDITWHEEL_REPAIR_OPTIONS="$(cat $GITHUB_WORKSPACE/cibuildwheel/exclude_list.txt | sed -e "s/.*/--exclude &/" | xargs)"
echo "AUDITWHEEL_REPAIR_OPTIONS=\"$AUDITWHEEL_REPAIR_OPTIONS\"" >> "$GITHUB_ENV"