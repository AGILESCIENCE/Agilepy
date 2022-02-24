#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

rm -f $script_dir/../.coverage

echo "Script dir: $script_dir"

agilepy_path=$((python "$script_dir/get_agilepy_path.py") 2>&1)

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

  pytest --disable-warnings \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         "$agilepy_path/testing/unittesting/utils"

  pytest --disable-warnings \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         "$agilepy_path/testing/unittesting/config"

  pytest --disable-warnings \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         "$agilepy_path/testing/unittesting/core"
  
  pytest --disable-warnings \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         "$agilepy_path/testing/unittesting/api"
  
fi
