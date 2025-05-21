#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# Usage and help function
usage() {
  echo "Usage: $0 [BASE_VERSION] [AGILEPY_RELEASE]"
  echo
  echo "Build the Agilepy Docker image."
  echo
  echo "Arguments:"
  echo "  BASE_VERSION     The tag of agilepy-recipe to use (e.g., BUILD26)"
  echo "  AGILEPY_RELEASE  The Agilepy release tag, branch or commit to use for the build process (e.g., v1.6.4 or develop)"
  echo "  IMAGE_TAG        The tag to assign to the built Docker image (e.g., latest, v1.6.4)"
  echo
  echo "Options:"
  echo "  -h, --help        Show this help message and exit"
}

# Helper for -h or --help
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 3 ]]; then
  echo "Error: Invalid number of arguments."
  usage
  exit 1
fi

# Script Directory: Agilepy/docker. Parent Directory: Agilepy
SCRIPT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PARENT_DIRECTORY="$(dirname "$SCRIPT_DIRECTORY")"

# Arguments
BASE_VERSION=$1
AGILEPY_RELEASE=$2
IMAGE_TAG=$3

echo "docker build --no-cache \
  -f "$SCRIPT_DIRECTORY"/recipes/agilepy/Dockerfile \
  --build-arg BASE_VERSION="$BASE_VERSION" \
  --build-arg AGILEPY_RELEASE="$AGILEPY_RELEASE" \
  -t agilescience/agilepy:"$IMAGE_TAG" \
  $PARENT_DIRECTORY"

# Execution
docker build --no-cache \
  -f $SCRIPT_DIRECTORY/recipes/agilepy/Dockerfile \
  --build-arg BASE_VERSION="$BASE_VERSION" \
  --build-arg AGILEPY_RELEASE="$AGILEPY_RELEASE" \
  -t agilescience/agilepy:$IMAGE_TAG \
  $PARENT_DIRECTORY
