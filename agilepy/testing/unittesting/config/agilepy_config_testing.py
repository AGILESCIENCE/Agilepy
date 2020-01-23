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


class AgilepyConfigUnittesting(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/config"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=False)

    def test_validation_tmin_not_in_index(self):

        self.config.setOptions(tmin=456361777)

        error_dict = self.config._validateConfiguration(self.config.conf)

        self.assertEqual(True, "input/tmin" in error_dict)
        self.assertEqual(1, len(error_dict))

    def test_validation_tmax_not_in_index(self):

        self.config.setOptions(tmax=456537946)

        error_dict = self.config._validateConfiguration(self.config.conf)

        self.assertEqual(True, "input/tmax" in error_dict)
        self.assertEqual(1, len(error_dict))


if __name__ == '__main__':
    unittest.main()
