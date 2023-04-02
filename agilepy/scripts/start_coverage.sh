#!/bin/bash

agilepy_path=$(python -c "import agilepy as _; print(_.__path__[0])")

if [ $? -ne 0 ]; then
  printf "\n\33[31mGetting Agilepy installation dir failed ($?) !\33[0m\n"
  exit 126
else
  printf "\n\33[32mAgilepy is installed in: $agilepy_path\33[0m\n"

  pytest --disable-warnings -v \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         "$agilepy_path/testing/unittesting/utils"

  pytest --disable-warnings -v \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         "$agilepy_path/testing/unittesting/config"

  pytest --disable-warnings -v \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         "$agilepy_path/testing/unittesting/core"
  
  pytest --disable-warnings -v \
         --cov-config="$agilepy_path/testing/unittesting/coverage/.coveragerc" \
         --cov-report "html:$agilepy_path/testing/unittesting/coverage/cov_html_report" \
         --cov-report "xml:$agilepy_path/testing/unittesting/coverage/cov_xml_report" \
         --cov=agilepy \
         --cov-append \
         "$agilepy_path/testing/unittesting/api"
  
fi
