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
                                           CannotSetNotUpdatableOptionError, \
                                           ConfigurationsNotValidError


class AgilepyConfigUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/config"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)


    def test_validation_tmin_not_in_index(self):

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, tmin=456361777, timetype="TT")



    def test_validation_tmax_not_in_index(self):

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, tmax=456537946, timetype="TT")


    def test_validation_min_max(self):

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, fovradmin=10, fovradmax=0)
        self.assertRaises(ConfigurationsNotValidError, self.config.setOptions, emin=10, emax=0)



    def test_set_options(self):

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        # float instead of int is ok.
        self.assertEqual(None, self.config.setOptions(tmin=456361779, timetype="TT"))


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


    def test_energybins(self):

        self.config = AgilepyConfig()

        # galcoeff and isocoeff are None
        conf1Path = os.path.join(self.currentDirPath,"conf/conf1.yaml")

        self.config.loadConfigurations(conf1Path)

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


    def test_bkg_coeff(self):

        self.config = AgilepyConfig()

        # galcoeff and isocoeff are None
        conf1Path = os.path.join(self.currentDirPath,"conf/conf1.yaml")

        self.config.loadConfigurations(conf1Path, validate=False)

        self.assertEqual(2, len(self.config.getOptionValue("isocoeff")))
        self.assertEqual(2, len(self.config.getOptionValue("galcoeff")))

        for i in range(2):
            self.assertEqual(-1, self.config.getOptionValue("isocoeff")[i])
            self.assertEqual(-1, self.config.getOptionValue("galcoeff")[i])




        # galcoeff isocoeff are lists
        conf1Path = os.path.join(self.currentDirPath,"conf/conf2.yaml")

        self.config.loadConfigurations(conf1Path, validate=False)

        self.assertEqual(2, len(self.config.getOptionValue("isocoeff")))
        self.assertEqual(2, len(self.config.getOptionValue("galcoeff")))

        self.assertEqual(10, self.config.getOptionValue("isocoeff")[0])
        self.assertEqual(15, self.config.getOptionValue("isocoeff")[1])
        self.assertEqual(0.6, self.config.getOptionValue("galcoeff")[0])
        self.assertEqual(0.8, self.config.getOptionValue("galcoeff")[1])


        # galcoeff and isocoeff are changed at runtime

        self.config.setOptions(isocoeff=[10, 15], galcoeff=[0.6, 0.8])
        self.assertEqual(10, self.config.getOptionValue("isocoeff")[0])
        self.assertEqual(15, self.config.getOptionValue("isocoeff")[1])
        self.assertEqual(0.6, self.config.getOptionValue("galcoeff")[0])
        self.assertEqual(0.8, self.config.getOptionValue("galcoeff")[1])

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

        self.config.loadConfigurations(conf1Path, validate=False)

        self.assertEqual(5.99147, self.config.getOptionValue("loccl"))

        self.config.setOptions(loccl=99)

        self.assertEqual(9.21034, self.config.getOptionValue("loccl"))

        self.assertEqual(2, len(self.config.getOptionValue("isocoeff")))
        self.assertEqual(2, len(self.config.getOptionValue("galcoeff")))



        conf2Path = os.path.join(self.currentDirPath,"conf/conf2.yaml")

        self.config.loadConfigurations(conf2Path, validate=False)

        self.assertEqual(9.21034, self.config.getOptionValue("loccl"))


if __name__ == '__main__':
    unittest.main()
