# DESCRIPTION
#       Agilepy software
#
# NOTICE
#      Any information contained in this software
#      is property of the AGILE TEAM and is strictly
#      private and confidential.
#      Copyright (C) 2005-2020 AGILE Team.
#          Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
#          Addis Antonio <antonio.addis@inaf.it>
#          Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
#          Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
#      All rights reserved.

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.


import pytest
import os

from agilepy.core.AGBaseAnalysis import AGBaseAnalysis
from agilepy.core.CustomExceptions import ConfigurationsNotValidError, ConfigFileOptionTypeError, OptionNotFoundInConfigFileError


@pytest.mark.bayesianblocks
class TestAGBayesianBlocksConfig():

    @pytest.mark.testlogsdir("config/test_logs/config_bb_null")
    @pytest.mark.testconfig("config/conf/conf_bb_null.yaml")
    def test_config_bb_null(self, config, environ_test_logs_dir):
        """Test that all null input files raise an error."""
        ag_base = AGBaseAnalysis(config)
        with pytest.raises(ConfigurationsNotValidError):
            ag_base.config.loadConfigurationsForClass("AGBayesianBlocks")

            
    @pytest.mark.testlogsdir("config/test_logs/config_bb")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_config_BB(self, config, environ_test_logs_dir, testdata):
        """Test that a standard configuration works."""
        ag_base = AGBaseAnalysis(config)
        ag_base.config.loadConfigurationsForClass("AGBayesianBlocks")
        
        # Check that file_path read from file is the same provided in the test marker
        assert ag_base.getOption("file_path") == testdata
        # Check that Completion Strategies expanded the path
        assert "$" not in ag_base.getOption("file_path")
        
        # Check that methods of mother classes work
        assert ag_base.config.getSectionOfOption("file_path")=="selection"
        assert ag_base.config.getOptionValue("file_path") == testdata
        
        # Test option setting with good and bad values
        assert ag_base.getOption("useerror") == True
        ag_base.config.setOptions(useerror=False)
        assert ag_base.getOption("useerror") == False
        
        with pytest.raises(ConfigFileOptionTypeError):
            ag_base.config.setOptions(ratecorrection="not_a_bool")
        with pytest.raises(OptionNotFoundInConfigFileError):
            ag_base.config.setOptions(rate="not_a_bool")


        # Test various methods
        config = ag_base.config.getConf()
        assert config["selection"]["file_path"] == testdata
        config = ag_base.config.getConf(key="selection")
        assert config["file_path"] == testdata
        config = ag_base.config.getConf(key="selection", subkey="file_path")
        assert config == testdata
        
        ag_base.printOptions()
        
        # Test output directory, which in this case is subfolder of TEST_LOGS_DIR
        assert os.environ['TEST_LOGS_DIR'] in ag_base.getAnalysisDir()
    
    
    @pytest.mark.testlogsdir("config/test_logs/config_bb_miss")
    @pytest.mark.testconfig("config/conf/conf_bb_missingkeys.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_config_bb_miss(self, config, environ_test_logs_dir, testdata):
        """Test that missing keys are dealt with."""
        ag_base = AGBaseAnalysis(config)
        ag_base.config.loadConfigurationsForClass("AGBayesianBlocks")
        
        assert ag_base.getOption("file_path") == testdata
        
        # Test the Config Default values for selection and bayesianblocks sections
        config = ag_base.config.getConf()
        assert config['selection']['file_mode'] == "agile_ap"
        assert config['selection']['ratecorrection'] == 0
        assert config['selection']['tstart'  ] == None
        assert config['selection']['tstop'   ] == None
        assert config['bayesianblocks']['fitness' ] == "events"
        assert config['bayesianblocks']['useerror'] == True
        assert config['bayesianblocks']['gamma'   ] == None
        assert config['bayesianblocks']['p0'      ] == None
        
        

