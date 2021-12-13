#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

rm -f $script_dir/../.coverage

pytest --disable-warnings \
       --cov-config="$script_dir/../testing/unittesting/coverage/.coveragerc" \
       --cov-report "html:$script_dir/../testing/unittesting/coverage/cov_html_report" \
       --cov-report "xml:$script_dir/../testing/unittesting/coverage/cov_xml_report" \
       --cov=agilepy \
       --cov-append \
       "$script_dir/../testing/unittesting/utils"

pytest --disable-warnings \
       --cov-config="$script_dir/../testing/unittesting/coverage/.coveragerc" \
       --cov-report "html:$script_dir/../testing/unittesting/coverage/cov_html_report" \
       --cov-report "xml:$script_dir/../testing/unittesting/coverage/cov_xml_report" \
       --cov=agilepy \
       --cov-append \
       "$script_dir/../testing/unittesting/config"

pytest --disable-warnings \
       --cov-config="$script_dir/../testing/unittesting/coverage/.coveragerc" \
       --cov-report "html:$script_dir/../testing/unittesting/coverage/cov_html_report" \
       --cov-report "xml:$script_dir/../testing/unittesting/coverage/cov_xml_report" \
       --cov=agilepy \
       --cov-append \
       "$script_dir/../testing/unittesting/core"

pytest --disable-warnings \
       --cov-config="$script_dir/../testing/unittesting/coverage/.coveragerc" \
       --cov-report "html:$script_dir/../testing/unittesting/coverage/cov_html_report" \
       --cov-report "xml:$script_dir/../testing/unittesting/coverage/cov_xml_report" \
       --cov=agilepy.api \
       --cov-append \
       "$script_dir/../testing/unittesting/api"
