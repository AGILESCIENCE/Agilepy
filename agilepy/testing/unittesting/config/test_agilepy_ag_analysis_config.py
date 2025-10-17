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


import os
import shutil
import pytest
from pathlib import Path

from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.core.CustomExceptions import OptionNotFoundInConfigFileError, ConfigFileOptionTypeError, CannotSetHiddenOptionError, CannotSetNotUpdatableOptionError, ConfigurationsNotValidError, OptionNameNotSupportedError, DeprecatedOptionError

@pytest.fixture(autouse=True)
def clean_test_env():
    """Fixture to clean output dir before each test."""
    current_dir_path = Path(__file__).parent.absolute()
    agilepyconf_path = os.path.join(current_dir_path, "conf/agilepyconf.yaml")
    out_dir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/config"))
    if out_dir.exists() and out_dir.is_dir():
        shutil.rmtree(out_dir)
    yield

@pytest.mark.new
class TestAGAnalysisConfig(): 

    def test_validation_min_max(self):
        config = AgilepyConfig()
        config.loadBaseConfigurations(os.path.join(Path(__file__).parent, "conf/agilepyconf.yaml"))
        config.loadConfigurationsForClass("AGAnalysis")

        with pytest.raises(ConfigurationsNotValidError):
            config.setOptions(dq=0, fovradmin=10, fovradmax=0)


    def test_set_options(self):
        config = AgilepyConfig()
        config.loadBaseConfigurations(os.path.join(Path(__file__).parent, "conf/agilepyconf.yaml"))
        config.loadConfigurationsForClass("AGAnalysis")

        # float instead of int is ok.
        assert config.setOptions(tmin=433857532., tmax=435153532., timetype="TT") is None
        assert config.getOptionValue("timetype") == "TT"

        assert config.setOptions(tmin=58026.5, tmax=58027.5, timetype="MJD") is None
        assert config.getOptionValue("timetype") == "MJD"

        with pytest.raises(CannotSetNotUpdatableOptionError):
            config.setOptions(tmin=58026.5)  # we must pass also timetype

        with pytest.raises(CannotSetNotUpdatableOptionError):
            config.setOptions(verboselvl=2)

        with pytest.raises(OptionNotFoundInConfigFileError):
            config.setOptions(pdor="kmer")

        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(minimizertype=666)
        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(energybins=[1, 2, 3])
        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(energybins=666)
        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(energybins="100, 300")
        
        # with pytest.raises(CannotSetHiddenOptionError):
        #     config.setOptions(lonpole=100)  # deprecated

        # len(energybins) = 2
        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(galcoeff=0.617196)
        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(isocoeff=0.617196)

        with pytest.raises(ConfigurationsNotValidError):
            config.setOptions(galcoeff=[0.617196])
        with pytest.raises(ConfigurationsNotValidError):
            config.setOptions(isocoeff=[0.617196])

        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(fluxcorrection=3.14)

        with pytest.raises(ConfigurationsNotValidError):
            config.setOptions(fluxcorrection=25)

        with pytest.raises(DeprecatedOptionError):
            config.setOptions(emin=100)



    def test_validation_wrong_AGAnalysis(self):
        """Test that reading a not valid configuration file raises an error."""
        config = AgilepyConfig()
        conf_path = os.path.join(Path(__file__).parent, "conf/conf_notvalid.yaml")
        config.loadBaseConfigurations(conf_path)
        with pytest.raises(ConfigurationsNotValidError):
            config.loadConfigurationsForClass("AGAnalysis")

    def test_energybins(self):

        config = AgilepyConfig()
        # galcoeff and isocoeff are None
        conf1Path = os.path.join(Path(__file__).parent, "conf/conf1.yaml")
        config.loadBaseConfigurations(conf1Path)
        config.loadConfigurationsForClass("AGAnalysis")
        
        assert config.getOptionValue("energybins")[0][0] == 100
        assert config.getOptionValue("energybins")[0][1] == 300
        assert config.getOptionValue("energybins")[1][0] == 300
        assert config.getOptionValue("energybins")[1][1] == 1000

        config.setOptions(energybins=[[200, 400], [400, 1000]])

        assert config.getOptionValue("energybins")[0][0] == 200
        assert config.getOptionValue("energybins")[0][1] == 400
        assert config.getOptionValue("energybins")[1][0] == 400
        assert config.getOptionValue("energybins")[1][1] == 1000

        # wrong type
        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(energybins=["[200, 400]", "[400, 1000]"])

        # galcoeff and isocoeff are None and len(energybins) = 1
        conf3Path = os.path.join(Path(__file__).parent, "conf/conf3.yaml")
        config.loadBaseConfigurations(conf3Path)
        config.loadConfigurationsForClass("AGAnalysis")

        assert config.getOptionValue("energybins")[0][0] == 100
        assert config.getOptionValue("energybins")[0][1] == 300

        config.setOptions(energybins=[[200, 400], [400, 1000]])


    def test_bkg_coeff(self):

        config = AgilepyConfig()

        # galcoeff and isocoeff are None
        conf1Path = os.path.join(Path(__file__).parent, "conf/conf1.yaml")

        config.loadBaseConfigurations(conf1Path)
        config.loadConfigurationsForClass("AGAnalysis")

        assert len(config.getOptionValue("isocoeff")) == 4
        assert len(config.getOptionValue("galcoeff")) == 4

        for i in range(4):
            assert config.getOptionValue("isocoeff")[i] == -1
            assert config.getOptionValue("galcoeff")[i] == -1




        # galcoeff isocoeff are lists
        conf1Path = os.path.join(Path(__file__).parent, "conf/conf2.yaml")

        config.loadBaseConfigurations(conf1Path)
        config.loadConfigurationsForClass("AGAnalysis")

        assert len(config.getOptionValue("isocoeff")) == 4
        assert len(config.getOptionValue("galcoeff")) == 4

        assert config.getOptionValue("isocoeff")[0] == 10
        assert config.getOptionValue("isocoeff")[1] == 15
        assert config.getOptionValue("galcoeff")[0] == 0.6
        assert config.getOptionValue("galcoeff")[1] == 0.8


        # galcoeff and isocoeff are changed at runtime
        config.setOptions(isocoeff=[10, 15, 10, 15], galcoeff=[0.6, 0.8, 0.6, 0.8])
        assert config.getOptionValue("isocoeff") == [10, 15, 10, 15]
        assert config.getOptionValue("galcoeff") == [0.6, 0.8, 0.6, 0.8]

        # this should cause an error because len(energybins) == 2
        with pytest.raises(ConfigurationsNotValidError):
            config.setOptions(isocoeff=[10])
        with pytest.raises(ConfigurationsNotValidError):
            config.setOptions(galcoeff=[0.6])

        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(isocoeff=None, galcoeff=None)

        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(isocoeff="Pluto", galcoeff="Pippo")

        # this should create an error!!
        with pytest.raises(ConfigFileOptionTypeError):
            config.setOptions(isocoeff=["Pluto"], galcoeff=["Pippo"])



    def test_complete_configuration(self):

        config = AgilepyConfig()
        conf1Path = os.path.join(Path(__file__).parent, "conf/conf1.yaml")
        config.loadBaseConfigurations(conf1Path)
        config.loadConfigurationsForClass("AGAnalysis")

        assert config.getOptionValue("loccl") == 5.99147
        config.setOptions(loccl=99)
        assert config.getOptionValue("loccl") == 9.21034
        assert len(config.getOptionValue("isocoeff")) == 4
        assert len(config.getOptionValue("galcoeff")) == 4



        conf2Path = os.path.join(Path(__file__).parent, "conf/conf2.yaml")
        config.loadBaseConfigurations(conf2Path)
        config.loadConfigurationsForClass("AGAnalysis")

        assert config.getOptionValue("loccl") == 9.21034



    def test_evt_log_files_env_vars(self):

        config = AgilepyConfig()
        conf1Path = os.path.join(Path(__file__).parent, "conf/conf1.yaml")
        config.loadBaseConfigurations(conf1Path)
        config.loadConfigurationsForClass("AGAnalysis")

        assert "$" not in config.getOptionValue("evtfile")
        assert "$" not in config.getOptionValue("logfile")

        config.setOptions(
            evtfile="$AGILE/agilepy-test-data/test_dataset_6.0/EVT/EVT.index",
            logfile="$AGILE/agilepy-test-data/test_dataset_6.0/LOG/LOG.index",
        )
        assert "$" not in config.getOptionValue("evtfile")
        assert "$" not in config.getOptionValue("logfile")

    
    def test_datapath_restapi(self):
        
        config = AgilepyConfig()

        conf1Path = os.path.join(Path(__file__).parent, "conf/conf1.yaml")

        config.loadBaseConfigurations(conf1Path)
        config.loadConfigurationsForClass("AGAnalysis")

        with pytest.raises(CannotSetNotUpdatableOptionError):
            config.setOptions(datapath="/foo/bar")
        with pytest.raises(CannotSetNotUpdatableOptionError):
            config.setOptions(userestapi=True)

    def test_set_evtlog_ifdatapath(self, tmp_path):
        config = AgilepyConfig()

        conf1Path = os.path.join(Path(__file__).parent, "conf/conf4.yaml")
        
        dirpath = tmp_path / "foo" / "bar"
        dirpath.mkdir(parents=True, exist_ok=True)

        config.loadBaseConfigurations(conf1Path)
        config.loadConfigurationsForClass("AGAnalysis")

        assert config.getOptionValue("evtfile") == Path(config.getOptionValue("datapath")).joinpath("EVT.index")
        assert config.getOptionValue("logfile") == Path(config.getOptionValue("datapath")).joinpath("LOG.index")

        dirpath.rmdir()

