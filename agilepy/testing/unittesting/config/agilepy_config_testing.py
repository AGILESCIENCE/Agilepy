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


import unittest
from pathlib import Path
import os
import shutil

from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.utils.CustomExceptions import OptionNotFoundInConfigFileError, \
                                           ConfigFileOptionTypeError, \
                                           CannotSetHiddenOptionError, \
                                           CannotSetNotUpdatableOptionError


class AgilepyConfigUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")
        self.agilepyconfPathTestCompleteConf = os.path.join(self.currentDirPath,"conf/agilepyconf_test_complete_conf.yaml")

        outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/config"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)


    def test_validation_tmin_not_in_index(self):

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        self.config.setOptions(tmin=456361777)

        error_dict = self.config._validateConfiguration(self.config.conf)

        self.assertEqual(True, "input/tmin" in error_dict)
        self.assertEqual(1, len(error_dict))

    def test_validation_tmax_not_in_index(self):

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        self.config.setOptions(tmax=456537946)

        error_dict = self.config._validateConfiguration(self.config.conf)

        self.assertEqual(True, "input/tmax" in error_dict)
        self.assertEqual(1, len(error_dict))

    def test_validation_min_max(self):

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        self.config.setOptions(fovradmin=10, fovradmax=0, emin=10, emax=0)

        error_dict = self.config._validateConfiguration(self.config.conf)

        self.assertEqual(True, "selection/fovradmin" in error_dict)
        self.assertEqual(True, "selection/emin" in error_dict)

        self.assertEqual(2, len(error_dict))

    def test_set_options(self):

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        # float instead of int is ok.
        self.assertEqual(None, self.config.setOptions(tmin=456361777))

        self.assertRaises(CannotSetNotUpdatableOptionError, self.config.setOptions, verboselvl=2)
        self.assertRaises(CannotSetNotUpdatableOptionError, self.config.setOptions, logfilenameprefix="pippo")

        self.assertRaises(OptionNotFoundInConfigFileError, self.config.setOptions(), pdor="kmer")

        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions(), minimizertype=666)
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions(), energybins=[1,2,3])
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions(), energybins=666)
        self.assertRaises(ConfigFileOptionTypeError, self.config.setOptions(), energybins="100, 300")

        self.assertRaises(CannotSetHiddenOptionError, self.config.setOptions(), lonpole=100)

        self.assertEqual(None, self.config.setOptions(galcoeff=[0.617196]))
        self.assertEqual(None, self.config.setOptions(galcoeff=0.617196))
        self.assertEqual(None, self.config.setOptions(isocoeff=[0.617196]))
        self.assertEqual(None, self.config.setOptions(isocoeff=0.617196))

        """
        self.assertEqual(None, self.config.setOptions(evtfile="/data/input.evt"))
        self.assertEqual(None, self.config.setOptions(energybins=[[100, 300], [300, 1000]]))
        """
    def test_complete_configuration(self):

        self.config = AgilepyConfig()

        self.config.loadConfigurations(self.agilepyconfPathTestCompleteConf, validate=False)

        self.assertEqual(5.99147, self.config.getOptionValue("loccl"))

        self.config.setOptions(loccl=99)

        self.assertEqual(9.21034, self.config.getOptionValue("loccl"))

        self.assertEqual(2, len(self.config.getOptionValue("isocoeff")))
        self.assertEqual(2, len(self.config.getOptionValue("galcoeff")))



if __name__ == '__main__':
    unittest.main()
