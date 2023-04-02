#!/bin/bash

set -u
set -v
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $SCRIPT_DIR/utilities.sh

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <agilepy-recipe image tag: https://hub.docker.com/repository/docker/agilescience/agilepy-recipe>"
else
    boostrap agilepy-recipe $1
fi

