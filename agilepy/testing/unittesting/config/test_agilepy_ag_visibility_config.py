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

from astropy.time import Time
from pathlib import Path

from agilepy.core.AGBaseAnalysis import AGBaseAnalysis
from agilepy.core.CustomExceptions import ConfigurationsNotValidError, ConfigFileOptionTypeError, OptionNotFoundInConfigFileError, CannotSetNotUpdatableOptionError
from agilepy.utils.AstroUtils import AstroUtils

@pytest.mark.visibility
class TestAGVisibilityConfig():
    
    @pytest.mark.testlogsdir("config/test_logs/config_vis_null")
    @pytest.mark.testconfig("config/conf/conf_vis_null.yaml")
    def test_config_rm_null(self, config, environ_test_logs_dir):
        """Test that all null input files raise an error."""
        ag_base = AGBaseAnalysis(config)
        with pytest.raises(ConfigurationsNotValidError):
            ag_base.config.loadConfigurationsForClass("AGVisibility")
    
    @pytest.mark.testlogsdir("config/test_logs/config_vis")
    @pytest.mark.testconfig("api/conf/conf_visibility_3C454.3.yaml")
    def test_config_rm(self, config, environ_test_logs_dir):
        """Test that a standard configuration works."""
        ag_base = AGBaseAnalysis(config)
        ag_base.config.loadConfigurationsForClass("AGVisibility")
        
        AGILE_DIR = os.environ['AGILE']
        testdata = Path(AGILE_DIR).joinpath("agilepy-test-data/test_dataset_agn/LOG/LOG.index")
        fermidata= Path(AGILE_DIR).joinpath("agilepy-test-data/visibility/Fermi_test_SC00.fits")
        
        # Test input data
        assert ag_base.config.getSectionOfOption("logfile")=="input"
        assert ag_base.config.getOptionValue("logfile") == str(testdata)
        assert ag_base.getOption("logfile") == str(testdata)
        assert "$" not in ag_base.getOption("logfile")
        
        # Test Values
        assert str(environ_test_logs_dir) in ag_base.getAnalysisDir()
        assert ag_base.getOption("fermi_spacecraft_file") == str(fermidata)
        
        assert ag_base.getOption("timetype") == "TT"
        assert ag_base.getOption("step") == pytest.approx(30, rel=1e-6)
        assert ag_base.getOption("tmin") == pytest.approx(104371200, rel=1e-6)
        assert ag_base.getOption("tmax") == pytest.approx(632620800, rel=1e-6)
        
        assert ag_base.getOption("frame") == "icrs"
        assert ag_base.getOption("coord1") is None
        assert ag_base.getOption("coord2") is None
        
        # Test various methods
        config = ag_base.config.getConf()
        assert config["input"]["logfile"] == str(testdata)
        config = ag_base.config.getConf(key="input")
        assert config["logfile"] == str(testdata)
        config = ag_base.config.getConf(key="input", subkey="logfile")
        assert config == str(testdata)
        
        ag_base.printOptions()
        
        # Test output directory, which in this case is subfolder of TEST_LOGS_DIR
        assert os.environ['TEST_LOGS_DIR'] in ag_base.getAnalysisDir()
        
        # Test option setting with good and bad values
        ag_base.setOptions(coord1=343.496, coord2=16.151, frame='icrs')
        ag_base.setOptions(tmin=AstroUtils.convert_time_to_agile_seconds(Time(55513, format='mjd')),
                          tmax=AstroUtils.convert_time_to_agile_seconds(Time(55521, format='mjd')),
                          timetype="TT"
                          )
        
        assert ag_base.getOption("tmin") == pytest.approx(216691200)
        assert ag_base.getOption("tmax") == pytest.approx(217382400)
        assert ag_base.getOption("coord1") == pytest.approx(343.496)
        assert ag_base.getOption("coord2") == pytest.approx(16.151)
        
        with pytest.raises(ConfigFileOptionTypeError):
            ag_base.config.setOptions(logfile=3)
        with pytest.raises(OptionNotFoundInConfigFileError):
            ag_base.config.setOptions(false_key="this_does_not_exist")
        
        # Test that pair options cannot be updated on their own
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(tmin=594047780)
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(tmax=594047780)
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(timetype="iso")
        
        # Test that Tmin and Tmax order is respected
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag_base.setOptions(tmin=3.0, tmax=-3.0)

    @pytest.mark.testlogsdir("config/test_logs/config_vis_bad")
    @pytest.mark.testconfig("config/conf/conf_vis_bad.yaml")
    def test_config_rm_bad(self, config, environ_test_logs_dir):
        """Test that a bad configuration with tmin>tmax raises an error."""
        ag_base = AGBaseAnalysis(config)
        with pytest.raises(ConfigurationsNotValidError):
            ag_base.config.loadConfigurationsForClass("AGVisibility")
        