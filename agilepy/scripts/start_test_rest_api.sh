#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

agilepy_path=$(python3 -c "import agilepy as _; print(_.__path__[0])")

if [ $? -ne 0 ]; then
  printf "\n\33[31mGetting Agilepy installation dir failed ($?) !\33[0m\n"
  exit 126
else
  printf "\n\33[32mAgilepy is installed in: $agilepy_path\33[0m\n"

  printf "\n\33[34mRunning only tests with REST API to SSDC: agilepy.utils and agilepy.core\33[0m\n"
  
  python3 -m pytest -x --disable-warnings -v \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         -m "ssdc" --runrest \
         "$agilepy_path/testing/unittesting/utils" \
         "$agilepy_path/testing/unittesting/core"

  printf "\n\33[32mCopying coverage report into $HOME\33[0m\n"
  cp -r "$agilepy_path/testing/unittesting/coverage/cov_xml_report" "$HOME/cov_xml_report"
fi