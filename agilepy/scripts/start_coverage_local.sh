#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

pytest --cov-config="$script_dir/../testing/unittesting/coverage/.coveragerc" \
       --cov-report "html:$script_dir/../testing/unittesting/coverage/cov_html_report" \
       --cov-report "xml:$script_dir/../testing/unittesting/coverage/cov_xml_report" \
       --cov-report= \
       --cov=agilepy.config \
       --cov-append \
       "$script_dir/../testing/unittesting/config"

pytest --cov-config="$script_dir/../testing/unittesting/coverage/.coveragerc" \
       --cov-report "html:$script_dir/../testing/unittesting/coverage/cov_html_report" \
       --cov-report "xml:$script_dir/../testing/unittesting/coverage/cov_xml_report" \
       --cov-report= \
       --cov=agilepy.utils \
       --cov-append \
       "$script_dir/../testing/unittesting/utils"


pytest --cov-config="$script_dir/../testing/unittesting/coverage/.coveragerc" \
       --cov-report "html:$script_dir/../testing/unittesting/coverage/cov_html_report" \
       --cov-report "xml:$script_dir/../testing/unittesting/coverage/cov_xml_report" \
       --cov-report= \
       --cov=agilepy.api,agilepy.core \
       --cov-append \
       "$script_dir/../testing/unittesting/api"


pytest --cov-config="$script_dir/../testing/unittesting/coverage/.coveragerc" \
       --cov-report "html:$script_dir/../testing/unittesting/coverage/cov_html_report" \
       --cov-report "xml:$script_dir/../testing/unittesting/coverage/cov_xml_report" \
       --cov-report= \
       --cov=agilepy.api,agilepy.core \
       --cov-append \
       "$script_dir/../testing/unittesting/core"

