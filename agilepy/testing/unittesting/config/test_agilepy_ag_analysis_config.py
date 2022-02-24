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


from genericpath import exists
import os
import shutil
import unittest
from pathlib import Path

from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.core.CustomExceptions import OptionNotFoundInConfigFileError, \
                                          ConfigFileOptionTypeError, \
                                          CannotSetHiddenOptionError, \
                                          CannotSetNotUpdatableOptionError, \
                                          ConfigurationsNotValidError, \
                                          OptionNameNotSupportedError


class AgilepyConfigUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/config"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

    
    ##### TEST NOT SUPPORTED AFTER REST FEATURE
    """
    def test_validation_tmin_not_in_index(self):

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyconfPath)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, tmin=40000000, tmax=433957532, timetype="TT")


    
    def test_validation_tmax_not_in_index(self):

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyconfPath)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions,
                          tmin=433900000, tmax=456537946, timetype="TT")
    """
 
    def test_validation_min_max(self):

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyconfPath)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, dq=0, fovradmin=10, fovradmax=0)
        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, emin=10, emax=0)



    def test_set_options(self):

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyconfPath)
        self.config.loadConfigurationsForClass("AGAnalysis")

        # float instead of int is ok.
        self.assertEqual(None, self.config.setOptions(tmin=433857532., tmax=435153532., timetype="TT"))

        self.assertEqual("TT", self.config.getOptionValue("timetype"))

        self.assertEqual(None, self.config.setOptions(tmin=58026.5, tmax=58027.5, timetype="MJD"))

        self.assertEqual("MJD", self.config.getOptionValue("timetype"))



        self.assertRaises(CannotSetNotUpdatableOptionError, self.config.setOptions, tmin=58026.5) # we must pass also timetype

        self.assertRaises(CannotSetNotUpdatableOptionError, self.config.setOptions, verboselvl=2)
        self.assertRaises(CannotSetNotUpdatableOptionError, self.config.setOptions, logfilenameprefix="pippo")

        self.assertRaises(OptionNotFoundInConfigFileError, self.config.setOptions(), pdor="kmer")

        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions(), minimizertype=666)
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions(), energybins=[1,2,3])
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions(), energybins=666)
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions(), energybins="100, 300")

        self.assertRaises(CannotSetHiddenOptionError, self.config.setOptions(), lonpole=100)

        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions, galcoeff=0.617196)
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions, isocoeff=0.617196)

        # len(energybins) = 2
        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, galcoeff=[0.617196])
        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, isocoeff=[0.617196])

        self.assertRaises(ConfigFileOptionTypeError,
                          self.config.setOptions, fluxcorrection=3.14)

        self.assertRaises(ConfigurationsNotValidError,
                          self.config.setOptions, fluxcorrection=25)


    def test_energybins(self):

        self.config = AgilepyConfig()

        # galcoeff and isocoeff are None
        conf1Path = os.path.join(self.currentDirPath,"conf/conf1.yaml")

        self.config.loadBaseConfigurations(conf1Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertEqual(100, self.config.getOptionValue("energybins")[0][0])
        self.assertEqual(300, self.config.getOptionValue("energybins")[0][1])
        self.assertEqual(300, self.config.getOptionValue("energybins")[1][0])
        self.assertEqual(1000, self.config.getOptionValue("energybins")[1][1])

        self.config.setOptions(energybins=[[200, 400], [400, 1000]])

        self.assertEqual(200, self.config.getOptionValue("energybins")[0][0])
        self.assertEqual(400, self.config.getOptionValue("energybins")[0][1])
        self.assertEqual(400, self.config.getOptionValue("energybins")[1][0])
        self.assertEqual(1000, self.config.getOptionValue("energybins")[1][1])

        # wrong type
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions, energybins=["[200, 400]", "[400, 1000]"])

        # wrong length
        # self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, energybins=[[200, 400]])

        # galcoeff and isocoeff are None and len(energybins) = 1
        conf3Path = os.path.join(self.currentDirPath,"conf/conf3.yaml")

        self.config.loadBaseConfigurations(conf3Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertEqual(100, self.config.getOptionValue("energybins")[0][0])
        self.assertEqual(300, self.config.getOptionValue("energybins")[0][1])

        self.config.setOptions(energybins=[[200, 400], [400, 1000]])


    def test_bkg_coeff(self):

        self.config = AgilepyConfig()

        # galcoeff and isocoeff are None
        conf1Path = os.path.join(self.currentDirPath,"conf/conf1.yaml")

        self.config.loadBaseConfigurations(conf1Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertEqual(4, len(self.config.getOptionValue("isocoeff")))
        self.assertEqual(4, len(self.config.getOptionValue("galcoeff")))

        for i in range(4):
            self.assertEqual(-1, self.config.getOptionValue("isocoeff")[i])
            self.assertEqual(-1, self.config.getOptionValue("galcoeff")[i])




        # galcoeff isocoeff are lists
        conf1Path = os.path.join(self.currentDirPath,"conf/conf2.yaml")

        self.config.loadBaseConfigurations(conf1Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertEqual(4, len(self.config.getOptionValue("isocoeff")))
        self.assertEqual(4, len(self.config.getOptionValue("galcoeff")))

        self.assertEqual(10, self.config.getOptionValue("isocoeff")[0])
        self.assertEqual(15, self.config.getOptionValue("isocoeff")[1])
        self.assertEqual(0.6, self.config.getOptionValue("galcoeff")[0])
        self.assertEqual(0.8, self.config.getOptionValue("galcoeff")[1])


        # galcoeff and isocoeff are changed at runtime

        self.config.setOptions(isocoeff=[10, 15, 10, 15], galcoeff=[0.6, 0.8, 0.6, 0.8])
        self.assertEqual(10, self.config.getOptionValue("isocoeff")[0])
        self.assertEqual(15, self.config.getOptionValue("isocoeff")[1])
        self.assertEqual(10, self.config.getOptionValue("isocoeff")[2])
        self.assertEqual(15, self.config.getOptionValue("isocoeff")[3])
        self.assertEqual(0.6, self.config.getOptionValue("galcoeff")[0])
        self.assertEqual(0.8, self.config.getOptionValue("galcoeff")[1])
        self.assertEqual(0.6, self.config.getOptionValue("galcoeff")[2])
        self.assertEqual(0.8, self.config.getOptionValue("galcoeff")[3])

        # this should cause an error because len(energybins) == 2
        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, isocoeff=[10])
        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, galcoeff=[0.6])

        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions, isocoeff=None, galcoeff=None)

        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions, isocoeff="Pluto", galcoeff="Pippo")

        # this should create an error!!
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions, isocoeff=["Pluto"], galcoeff=["Pippo"])




    def test_complete_configuration(self):

        self.config = AgilepyConfig()

        conf1Path = os.path.join(self.currentDirPath,"conf/conf1.yaml")

        self.config.loadBaseConfigurations(conf1Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertEqual(5.99147, self.config.getOptionValue("loccl"))

        self.config.setOptions(loccl=99)

        self.assertEqual(9.21034, self.config.getOptionValue("loccl"))

        self.assertEqual(4, len(self.config.getOptionValue("isocoeff")))
        self.assertEqual(4, len(self.config.getOptionValue("galcoeff")))



        conf2Path = os.path.join(self.currentDirPath,"conf/conf2.yaml")

        self.config.loadBaseConfigurations(conf2Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertEqual(9.21034, self.config.getOptionValue("loccl"))



    def test_evt_log_files_env_vars(self):

        self.config = AgilepyConfig()

        conf1Path = os.path.join(self.currentDirPath,"conf/conf1.yaml")

        self.config.loadBaseConfigurations(conf1Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertEqual(True, "$" not in self.config.getOptionValue("evtfile"))
        self.assertEqual(True, "$" not in self.config.getOptionValue("logfile"))

        self.config.setOptions(
                    evtfile="$AGILE/agilepy-test-data/test_dataset_6.0/EVT/EVT.index",
                    logfile="$AGILE/agilepy-test-data/test_dataset_6.0/LOG/LOG.index"
                )

        self.assertEqual(True, "$" not in self.config.getOptionValue("evtfile"))
        self.assertEqual(True, "$" not in self.config.getOptionValue("logfile"))

    
    def test_datapath_restapi(self):
        
        self.config = AgilepyConfig()

        conf1Path = os.path.join(self.currentDirPath,"conf/conf1.yaml")

        self.config.loadBaseConfigurations(conf1Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertRaises(CannotSetNotUpdatableOptionError, self.config.setOptions, datapath="/foo/bar")
        self.assertRaises(CannotSetNotUpdatableOptionError, self.config.setOptions, userestapi=True)

    def test_set_evtlog_ifdatapath(self):
        self.config = AgilepyConfig()

        conf1Path = os.path.join(self.currentDirPath,"conf/conf4.yaml")
        
        dirpath = Path("/tmp/foo/bar") 
        dirpath.mkdir(parents=True, exist_ok=True)

        self.config.loadBaseConfigurations(conf1Path)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertEqual(self.config.getOptionValue("evtfile"), Path(self.config.getOptionValue("datapath")).joinpath("EVT.index"))
        self.assertEqual(self.config.getOptionValue("logfile"), Path(self.config.getOptionValue("datapath")).joinpath("LOG.index"))

        dirpath.rmdir()

    ##### TEST NOT SUPPORTED AFTER REST FEATURE
    """
    def test_validation_tmin_not_in_index(self):

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyconfPath)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, tmin=40000000, tmax=433957532, timetype="TT")


    
    def test_validation_tmax_not_in_index(self):

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyconfPath)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions,
                          tmin=433900000, tmax=456537946, timetype="TT")
    """

if __name__ == '__main__':
    unittest.main()
