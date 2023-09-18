#!/bin/bash

set -u
set -v
set -e

if [ $# -ne 2 ]; then
    printf "\n\33[31m > bootstrap.sh <tag> <username> \33[0m\n\n"
else

    MY_UID="$(id -u)"
    MY_GID="$(id -g)"
    SDE_TAG=$1
    INTERMEDIATE_TAG=local/delete_me_soon:latest
    USERNAME=$2

    docker tag $SDE_TAG $INTERMEDIATE_TAG
    docker build \
        --tag $SDE_TAG\_$USERNAME \
        - <<EOF
FROM ${INTERMEDIATE_TAG}
USER root
RUN usermod -u "${MY_UID}" flareadvocate && groupmod -g "${MY_GID}" flareadvocate
USER flareadvocate
EOF
    docker rmi $INTERMEDIATE_TAG
fi
