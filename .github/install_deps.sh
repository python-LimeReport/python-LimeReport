#!/bin/bash

if [ "$(uname -m)" = "aarch64" ]; then
    apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libxslt1.1 libllvm11
fi