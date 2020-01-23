#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Script dir: $script_dir"

agilepy_path=$((python $script_dir/get_agilepy_path.py) 2>&1)

if [ $? -ne 0 ]; then
  echo "Getting agilepy library path => command failed."
  return;
fi


#if [ $# -eq 0 ]
#  then
#    echo "Please, enter the path to agilepy folder inside the anaconda distribution."
#    return;
#fi

OS=$(uname -s)

if [ $OS = "Darwin" ]; then
  echo "OSX detected"
else
  echo "Linux detected"
fi

echo "agilepy_path: "$agilepy_path



python $agilepy_path/testing/unittesting/api/ag_analysis_unit_testing.py -v
