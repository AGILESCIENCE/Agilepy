#!/bin/bash

if [ "$OS" = "Darwin" ]; then
  echo "OSX detected"
else
  echo "Linux detected"
fi

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Script dir: $script_dir"

python "$script_dir/../testing/unittesting/api/ag_mle_unit_test.py" -v
python "$script_dir/../testing/unittesting/api/sources_library_unit_test.py" -v
python "$script_dir/../testing/unittesting/config/agilepy_config_test.py" -v
python "$script_dir/../testing/unittesting/utils/utils_test.py" -v
