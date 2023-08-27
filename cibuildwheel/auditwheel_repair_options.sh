#!/bin/sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

AUDITWHEEL_REPAIR_OPTIONS="$(cat $SCRIPT_DIR/exclude_list.txt | sed -e "s/.*/--exclude &/" | xargs)"

echo "AUDITWHEEL_REPAIR_OPTIONS=\"$AUDITWHEEL_REPAIR_OPTIONS\""