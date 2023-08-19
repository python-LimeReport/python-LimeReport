#!/bin/bash

AQTINSTALL_VERSION=3.1.6
QT_VERSION=6.4.2

pipx install aqtinstall==${AQTINSTALL_VERSION}
aqt install-qt --outputdir /opt/Qt linux desktop ${QT_VERSION}