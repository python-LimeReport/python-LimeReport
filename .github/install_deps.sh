#!/bin/bash

if [ "$(uname -m)" = "aarch64" ]; then
    ldd -r $(which shiboken6)
    # apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libxslt1.1
fi