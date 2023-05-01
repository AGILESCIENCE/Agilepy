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
import unittest
import pytest
from pathlib import Path
from agilepy.utils.Utils import Utils
from agilepy.api.AGEngAgileOffaxisVisibility import AGEngAgileOffaxisVisibility

class TestAGEngAgileOffaxisVisibility:

    @pytest.mark.skip("To be fixed")
    @pytest.mark.testlogsdir("api/test_logs/test_compute_pointing_distances_from_source")
    @pytest.mark.testconfig("api/conf/agilepyconf_ageng.yaml")
    def test_compute_pointing_distances_from_source(self, config, logger):

        ageng = AGEngAgileOffaxisVisibility(config)

        # file = "/data/AGILE/LOG_INDEX/LOG.log.index"
        zmax = 60
        step = 10
        logfilesIndex = "$AGILE/agilepy-test-data/test_dataset_6.0/LOG/LOG.index"

        logfilesIndex = Utils._expandEnvVar(logfilesIndex)

        _, _, _, _, _, _, _, separationFile = ageng._computePointingDistancesFromSource(logfilesIndex, 456361778, 456373279, src_x=129.7, src_y=3.7, ref="gal", zmax=zmax, step=step, writeFiles=True)

        assert Path(separationFile).is_file()


    @pytest.mark.testlogsdir("api/test_logs/test_visibility_plot")
    @pytest.mark.testconfig("api/conf/agilepyconf_ageng.yaml")
    def test_visibility_plot(self, config, logger):

        ageng = AGEngAgileOffaxisVisibility(config)

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

        visplot, histoplot = ageng.visibilityPlot(logfilesIndex, 433900000, 433957532, src_x, src_y, ref, zmax, step, histogram, writeFiles, saveImage, fileFormat, title)

        assert Path(visplot).is_file()
        assert Path(histoplot).is_file()
