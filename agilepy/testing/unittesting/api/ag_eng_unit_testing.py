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

from agilepy.api.AGEng import AGEng

class AGEngUnittesting(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")
        self.outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/api"))

        if self.outDir.exists() and self.outDir.is_dir():
            shutil.rmtree(self.outDir)

        self.ageng = AGEng(self.agilepyconfPath)


    def test_compute_pointing_distances_from_source(self):

        # file = "/data/AGILE/LOG_INDEX/LOG.log.index"
        zmax = 60
        step = 10
        separations, ti_tt, tf_tt, ti_mjd, tf_mjd, src_ra, src_dec = self.ageng._computePointingDistancesFromSource(456361778, 456373279, src_x=129.7, src_y=3.7, ref="gal", zmax=zmax, step=step, logfilesIndex=None, writeFiles=True)

    def test_visibility_plot(self):

        src_x=129.7
        src_y=3.7
        ref="gal"
        zmax=60
        step=10
        logfilesIndex=None
        writeFiles=True
        saveImage=True
        format="png"
        title="Visibility plot 184075134 - 184275134"

        plotfilepath = self.ageng.visibilityPlot(456384273, 456426294, src_x, src_y, ref, zmax, step, writeFiles, logfilesIndex, saveImage, format, title)



if __name__ == '__main__':
    unittest.main()
