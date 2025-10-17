#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Install requirements
python3 -m pip install -r requirements.lock

# Install package
python3 -m pip install -e .

# Install test dataset
download_test_dataset.sh
