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
import pytest
from pathlib import Path

from agilepy.api.AGEngAgileFermiOffAxisVisibilityComparison import AGEngAgileFermiOffAxisVisibilityComparison

from agilepy.utils.Utils import Utils

class TestAGEngAgileFermiOffAxisVisibilityComparison:

    @pytest.fixture
    def log_dir(self):
        currentDirPath = Path(__file__).parent.absolute()
        test_logs_dir = Path(currentDirPath).joinpath("test_logs", "TestAGEngAgileFermiOffAxisVisibilityComparison")
        test_logs_dir.mkdir(parents=True, exist_ok=True)
        os.environ["TEST_LOGS_DIR"] = str(test_logs_dir)
        return test_logs_dir

    @pytest.fixture
    def conf(self):
        currentDirPath = Path(__file__).parent.absolute()
        return str(currentDirPath.joinpath("conf/agilepyconf_ageng.yaml"))

    def test_ap_offaxis_comparation(self, log_dir, conf):
        
        ageng = AGEngAgileFermiOffAxisVisibilityComparison(conf)


        time_windows = [[59861.55, 59861.65]]
        ra = 288.338178
        dec = 19.771496
        fermi_path = "/agilepy_development/SC00.fits"
        #agile_path = "/data01/ASDC_PROC3/DATA_ASDCe/INDEX/LOG.log.index"
        agile_path = "/ASDC_PROC2/DATA_2/INDEX/LOG.log.index"
        run = 50
        zmax = 80
        mode = "all"
        step = 1
        output_dirs = ageng.visibilityPlot(time_windows, ra, dec, fermi_path, agile_path, run, zmax, mode, step)            


        
        ap_agile = "/agilepy_development/ALL_10s_emin100_emax10000_r5_DQ0_FOV70.ap.ap4"
        ap_agile = "/agilepy_development/ALL_10s_emin100_emax10000_r5_DQ0_FOV70-Copy1.ap.ap4"
        ap_fermi = "/agilepy_development/lc_grb10sr5t0GRBconv.out"

        # We take the first time window from the time_windows list
        tstart = time_windows[0][0]
        tstop = time_windows[0][1]
        # We take the first vibility plot output directory, respectively 
        path_offaxis = output_dirs[0]

        # We highlight the whole interval
        lines = [[59861.55346063, 59861.58346063]]

        plotrate = True

        print(ap_agile, ap_fermi, tstart, tstop, path_offaxis, lines, plotrate)

        ageng.apOffaxisComparation(ap_agile, ap_fermi, tstart, tstop, path_offaxis, lines, plotrate)
        