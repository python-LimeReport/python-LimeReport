#!/bin/bash

if [  -n "$(uname -a | grep Ubuntu)" ]; then
    apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libxslt1.1
fi