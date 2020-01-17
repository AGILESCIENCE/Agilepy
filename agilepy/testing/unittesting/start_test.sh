#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

#python $script_dir/api/sources_library_unit_testing.py -v
python $script_dir/api/ag_analysis_unit_testing.py -v
