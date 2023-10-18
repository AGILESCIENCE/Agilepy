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

import pytest
from pathlib import Path

from agilepy.core.Parameters import Parameters

class TestParameters:

    def test_calibrationFiles(self):
        assert len(Parameters.getSupportedCalibrationFiles()) > 100

    def test_getSkyMap(self):
        skymap = Parameters.getSkyMap(10000, 50000, 5, "H0025")
        assert isinstance(skymap, Path)
        assert skymap.exists()
        assert skymap.name == "10000_50000.SKY002.SFMG_H0025.disp.conv.sky.gz"

    def test_getCalibrationMatrices(self):
        calibMatrices = Parameters.getCalibrationMatrices(5, "H0025")
        assert len(calibMatrices) == 3
        for matrix in calibMatrices:
            assert str(matrix).endswith(".gz")
            assert matrix.exists()

    def test_unsupportedIrf(self):
        with pytest.raises(ValueError):
            Parameters.getSkyMap(10000, 50000, 5, "XXX0025")
        with pytest.raises(ValueError):
            Parameters.getCalibrationMatrices(5, "XXX0025")
        