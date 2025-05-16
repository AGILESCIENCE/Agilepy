#!/bin/bash

if [ "$#" -ne 2 ]; then
    printf "Illegal number of parameters. Arguments: \n  type: local, gh\n  agilepy_tag\n"
else
  
  SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

  type="$1"

  export AGILEPY_TAG="$2"
  export PACKAGE_TAG="$2"

  if [ "$type" = "local" ]; then
    echo "Local build"
    folder="$SCRIPT_DIR"
  else
    echo "Devops build"
    folder="$SCRIPT_DIR/github-workflow-build"
  fi

  conda-build "$folder" -c agilescience
fi
