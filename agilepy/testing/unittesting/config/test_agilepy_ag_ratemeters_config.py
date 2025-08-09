# DESCRIPTION
#       Agilepy software
#
# NOTICE
#      Any information contained in this software
#      is property of the AGILE TEAM and is strictly
#      private and confidential.
#      Copyright (C) 2005-2020 AGILE Team.
#          Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
#          Panebianco Gabriele <gabriele.panebianco@inaf.it>
#          Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
#          Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
#          Addis Antonio <antonio.addis@inaf.it>
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
from agilepy.core.CustomExceptions import ConfigurationsNotValidError, ConfigFileOptionTypeError, OptionNotFoundInConfigFileError, CannotSetNotUpdatableOptionError


@pytest.mark.ratemeters
class TestAGRatemetersConfig():

    @pytest.mark.testlogsdir("config/test_logs/config_rm_null")
    @pytest.mark.testconfig("config/conf/conf_rm_null.yaml")
    def test_config_rm_null(self, config, environ_test_logs_dir):
        """Test that all null input files raise an error."""
        ag_base = AGBaseAnalysis(config)
        with pytest.raises(ConfigurationsNotValidError):
            ag_base.config.loadConfigurationsForClass("AGRatemeters")


    @pytest.mark.testlogsdir("config/test_logs/config_rm")
    @pytest.mark.testconfig("api/conf/agilepyconf_ratemeters.yaml")
    @pytest.mark.testdatafile("api/data/PKP080686_1_3913_000.lv1.cor.gz")
    def test_config_rm(self, config, environ_test_logs_dir, testdata):
        """Test that a standard configuration works."""
        ag_base = AGBaseAnalysis(config)
        ag_base.config.loadConfigurationsForClass("AGRatemeters")
        
        # Check that file_path read from file is the same provided in the test marker
        assert ag_base.getOption("file_path") == testdata
        # Check that Completion Strategies expanded the path
        assert "$" not in ag_base.getOption("file_path")
        # Check that methods of mother class work
        assert ag_base.config.getSectionOfOption("file_path")=="selection"
        assert ag_base.config.getOptionValue("file_path") == testdata
        
        # Test Values
        assert str(environ_test_logs_dir) in ag_base.getAnalysisDir()
        assert ag_base.getOption("timetype") == "TT"
        assert ag_base.getOption("T0") == pytest.approx(594047787, rel=1e-6)
        assert ag_base.getOption("background_tmin") == pytest.approx(-100.0, rel=1e-6)
        assert ag_base.getOption("background_tmax") == pytest.approx(-90.0, rel=1e-6)
        assert ag_base.getOption("signal_tmin") == pytest.approx(-1.0, rel=1e-6)
        assert ag_base.getOption("signal_tmax") == pytest.approx(3.0, rel=1e-6)
        
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
        
        # Test option setting with good and bad values
        ag_base.setOptions(signal_tmin=-2.0, signal_tmax=4.0)
        assert ag_base.getOption("signal_tmin") == pytest.approx(-2.0)
        assert ag_base.getOption("signal_tmax") == pytest.approx(+4.0)
        with pytest.raises(ConfigFileOptionTypeError):
            ag_base.config.setOptions(file_path=3)
        with pytest.raises(OptionNotFoundInConfigFileError):
            ag_base.config.setOptions(false_key="this_does_not_exist")
        
        # Test that pair options cannot be updated on their own
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(T0=594047780)
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(timetype="iso")
        
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(background_tmin=-3.0)
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(background_tmax=-3.0)
        
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(signal_tmin=-3.0)
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(signal_tmax=-3.0)
        
        # Test that Tmin and Tmax order is respected
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(signal_tmin=3.0, signal_tmax=-3.0)
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(background_tmin=3.0, background_tmax=-3.0)
        
    
    
    @pytest.mark.testlogsdir("config/test_logs/config_rm_miss")
    @pytest.mark.testconfig("config/conf/conf_rm_missingkeys.yaml")
    @pytest.mark.testdatafile("api/data/PKP080686_1_3913_000.lv1.cor.gz")
    def test_config_rm_miss(self, config, environ_test_logs_dir, testdata):
        """Test that missing keys are dealt with."""
        ag_base = AGBaseAnalysis(config)
        ag_base.config.loadConfigurationsForClass("AGRatemeters")
        
        # Mandatory fields
        assert ag_base.getOption("file_path") == testdata
        assert ag_base.getOption("timetype") == "TT"
        assert ag_base.getOption("T0") == pytest.approx(594047787, rel=1e-6)
        
        # Test the Config Default values
        config = ag_base.config.getConf()
        assert config['analysis']['background_tmin'] == pytest.approx(-4, rel=1e-6)
        assert config['analysis']['background_tmax'] == pytest.approx(-2, rel=1e-6)
        assert config['analysis']['signal_tmin'] == pytest.approx(-1, rel=1e-6)
        assert config['analysis']['signal_tmax'] == pytest.approx( 1, rel=1e-6)


    @pytest.mark.testlogsdir("config/test_logs/config_rm_bad")
    @pytest.mark.testconfig("config/conf/conf_rm_bad.yaml")
    def test_config_rm_bad(self, config, environ_test_logs_dir):
        """Test that a bad configuration with tmin>tmax raises an error."""
        ag_base = AGBaseAnalysis(config)
        with pytest.raises(ConfigurationsNotValidError):
            ag_base.config.loadConfigurationsForClass("AGRatemeters")
