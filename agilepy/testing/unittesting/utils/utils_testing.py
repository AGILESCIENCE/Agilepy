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
import unittest
from pathlib import Path
from time import sleep

from agilepy.utils.AstroUtils import AstroUtils
from agilepy.utils.AgilepyLogger import AgilepyLogger
from agilepy.config.AgilepyConfig import AgilepyConfig

class UtilsUnittesting(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

        self.agilepyLogger = AgilepyLogger()

        outDir = Path(self.config.getOptionValue("outdir"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

    def tearDown(self):
        self.agilepyLogger.reset()

    def test_initialize_logger_verboselvl_2(self):
        sleep(1.0)
        self.agilepyLogger.reset()
        self.config.setOptions(force=True, verboselvl=2)

        logfilePath = self.agilepyLogger.initialize(self.config.getOptionValue("outdir"), self.config.getOptionValue("logfilenameprefix"), self.config.getOptionValue("verboselvl"))

        self.assertEqual(True, logfilePath.is_file())

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            self.assertEqual(1, linesNumber)

        self.agilepyLogger.debug(self, "%s %s", "Debug", "message")
        self.agilepyLogger.info(self, "%s %s", "Info", "message")
        self.agilepyLogger.warning(self, "%s %s", "Warning", "message")
        self.agilepyLogger.critical(self, "%s %s", "Critical", "message")

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            self.assertEqual(5, linesNumber)


    def test_initialize_logger_verboselvl_1(self):
        sleep(1.0)
        self.agilepyLogger.reset()
        self.config.setOptions(force=True, verboselvl=1)

        logfilePath = self.agilepyLogger.initialize(self.config.getOptionValue("outdir"), self.config.getOptionValue("logfilenameprefix"), self.config.getOptionValue("verboselvl"))

        self.assertEqual(True, logfilePath.is_file())

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            self.assertEqual(1, linesNumber)

        self.agilepyLogger.debug(self, "%s %s", "Debug", "message")
        self.agilepyLogger.info(self, "%s %s", "Info", "message")
        self.agilepyLogger.warning(self, "%s %s", "Warning", "message")
        self.agilepyLogger.critical(self, "%s %s", "Critical", "message")

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            self.assertEqual(5, linesNumber)


    def test_initialize_logger_verboselvl_0(self):
        sleep(1.0)
        self.agilepyLogger.reset()
        self.config.setOptions(force=True, verboselvl=0)

        logfilePath = self.agilepyLogger.initialize(self.config.getOptionValue("outdir"), self.config.getOptionValue("logfilenameprefix"), self.config.getOptionValue("verboselvl"))

        self.assertEqual(True, logfilePath.is_file())

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            self.assertEqual(1, linesNumber)

        self.agilepyLogger.debug(self, "%s %s", "Debug", "message")
        self.agilepyLogger.info(self, "%s %s", "Info", "message")
        self.agilepyLogger.warning(self, "%s %s", "Warning", "message")
        self.agilepyLogger.critical(self, "%s %s", "Critical", "message")

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            self.assertEqual(5, linesNumber)

    def test_astro_utils_time_conversion(self):

        # checked on https://tools.ssdc.asi.it/conversionTools

        tt = AstroUtils.time_mjd_to_tt(58877.58596) #507391426.9439997

        tt_from_ssdc = 507391426.944
        self.assertEqual(True, tt_from_ssdc-tt<0.000001)

        mjd = AstroUtils.time_tt_to_mjd(507391426.9447)
        mjd_from_ssdc = 58877.58595999

        self.assertEqual(True, mjd_from_ssdc-mjd<0.000001)

if __name__ == '__main__':
    unittest.main()
