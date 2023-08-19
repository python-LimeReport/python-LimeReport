#!/bin/bash


pipx install aqtinstall==${AQTINSTALL_VERSION}
aqt install-qt --outputdir /opt/Qt linux desktop ${QT_VERSION}