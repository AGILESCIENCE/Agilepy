#!/bin/bash

# This file must be located in agilepy/scripts

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Script dir: $script_dir"

agilepy_path=$((python $script_dir/get_agilepy_path.py) 2>&1)

if [ $? -ne 0 ]; then
  echo "Getting agilepy library path => command failed."
  exit 126
else

  OS=$(uname -s)

  if [ "$OS" = "Darwin" ]; then
    echo "OSX detected"
  else
    echo "Linux detected"
  fi

  echo "agilepy_path: $agilepy_path/notebooks"

  jupyter notebook --notebook-dir="$agilepy_path/notebooks" "$agilepy_path/notebooks/agilepy-quickstart.ipynb"

fi
