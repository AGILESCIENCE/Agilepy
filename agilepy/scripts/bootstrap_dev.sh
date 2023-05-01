#!/bin/bash

set -u
set -v
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $SCRIPT_DIR/utilities.sh

export DUPLICATE_IMAGE=true 
export TAG="$1"

if [[ $# -ne 1 ]]; then
    printf "Usage: $0 <agilepy-recipe tag> \n -> tags: https://hub.docker.com/repository/docker/agilescience/agilepy-recipe"
else
    boostrap agilepy-recipe $TAG $DUPLICATE_IMAGE
fi

