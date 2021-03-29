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
import os
import shutil
from pathlib import Path

from agilepy.utils.Utils import Utils
from agilepy.api.AGEngAgileOffaxisVisibility import AGEngAgileOffaxisVisibility

class AGEngAgileOffaxisVisibilityUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()

        self.test_logs_dir = Path(self.currentDirPath).joinpath("test_logs", "AGEngAgileOffaxisVisibilityUT")
        self.test_logs_dir.mkdir(parents=True, exist_ok=True)
        os.environ["TEST_LOGS_DIR"] = str(self.test_logs_dir)


        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf_ageng.yaml")

        self.ageng = AGEngAgileOffaxisVisibility(self.agilepyconfPath)


    def test_compute_pointing_distances_from_source(self):

        # file = "/data/AGILE/LOG_INDEX/LOG.log.index"
        zmax = 60
        step = 10
        logfilesIndex = "$AGILE/agilepy-test-data/test_dataset_6.0/LOG/LOG.index"

        logfilesIndex = Utils._expandEnvVar(logfilesIndex)

        _, _, _, _, _, _, _, separationFile = self.ageng._computePointingDistancesFromSource(logfilesIndex, 456361778, 456373279, src_x=129.7, src_y=3.7, ref="gal", zmax=zmax, step=step, writeFiles=True)

        # self.assertEqual(True, os.path.isfile(separationFile))


    def test_visibility_plot(self):

        src_x=129.7
        src_y=3.7
        ref="gal"
        zmax=60
        step=10
        histogram=True
        writeFiles=True
        saveImage=True
        fileFormat="png"
        title="Visibility plot 184075134 - 184275134"

        logfilesIndex = "$AGILE/agilepy-test-data/test_dataset_6.0/LOG/LOG.index"

        visplot, histoplot = self.ageng.visibilityPlot(logfilesIndex, 433900000, 433957532, src_x, src_y, ref, zmax, step, histogram, writeFiles, saveImage, fileFormat, title)

        self.assertEqual(True, os.path.isfile(visplot))
        self.assertEqual(True, os.path.isfile(histoplot))


if __name__ == '__main__':
    unittest.main()
