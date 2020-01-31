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

  echo "agilepy_path: $agilepy_path"

  python "$agilepy_path/testing/unittesting/api/ag_analysis_unit_testing.py" -v
  python "$agilepy_path/testing/unittesting/api/sources_library_unit_testing.py" -v
  python "$agilepy_path/testing/unittesting/config/agilepy_config_testing.py" -v
  python "$agilepy_path/testing/unittesting/utils/utils_testing.py" -v


fi
