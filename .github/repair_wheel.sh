#!/bin/bash

SITE_PACKAGES=$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SITE_PACKAGES/PySide6:$SITE_PACKAGES/shiboken6 auditwheel -v repair $AUDITWHEEL_REPAIR_OPTIONS -w $1 $2