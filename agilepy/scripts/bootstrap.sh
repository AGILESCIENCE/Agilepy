#!/bin/bash

set -u
set -v
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $SCRIPT_DIR/utilities.sh

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <agilepy image tag: https://hub.docker.com/r/agilescience/agilepy/tags>"
else
    boostrap agilepy $1
fi

