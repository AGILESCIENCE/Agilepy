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
from os.path import Path
from agilepy.utils.Utils import Utils
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.api.AGEngDisplayComparison import AGEngDisplayComparison

class TestAGEngDisplayComparison:

    @pytest.fixture
    def get_log_dir(self):
        currentDirPath = Path(__file__).parent.absolute()
        test_logs_dir = Path(currentDirPath).joinpath("test_logs", "TestAGEngAgileFermiOffAxisVisibilityComparison")
        test_logs_dir.mkdir(parents=True, exist_ok=True)
        os.environ["TEST_LOGS_DIR"] = str(test_logs_dir)
        return test_logs_dir

    @pytest.fixture
    def get_conf(self):
        currentDirPath = Path(__file__).parent.absolute()
        return str(currentDirPath.joinpath("conf/agilepyconf_ageng.yaml"))

    @pytest.fixture
    def get_data_dir(self):
        currentDirPath = Path(__file__).parent.absolute()
        return currentDirPath.joinpath("data/test_ag_eng_agile_fermi_offaxis_visibility_comparison")

    def test_display_comparison_mjd(self, data_dir, conf):
        t0 = 59861.55346063
        time_windows = [(t0-120/86400, t0+1000/86400)]
        ra = 288.338178
        dec = 19.771496
        fermi_path = data_dir.joinpath("SC00.fits")
        agile_path = "/ASDC_PROC2/DATA_2/INDEX/LOG.log.index"
        run = 50
        zmax = 80
        mode = "all"
        step = 1
        data_column_name = "rate"
        vertical_boxes_mjd = [t0, t0+200/86400]
        ap_agile = data_dir.joinpath("ALL_10s_emin100_emax10000_r5_DQ0_FOV70.ap.ap4")
        ap_fermi = data_dir.joinpath("lc_grb10sr5t0GRBconv.out")
        tstart = time_windows[0][0]
        tstop = time_windows[0][1]
        time_range=time_windows[0]
        add_rm = True
        rm_files = [data_dir.joinpath("080412_RM-GRID_LC.txt"), data_dir.joinpath("080412_RM-AC0_LC.txt")]
        rm_labels = ['GRID', 'AC0']

        ageng = AGEngDisplayComparison(conf)

    
        
    def test_display_comparison_tt(self, data_dir, conf):
        t0 = 59861.55346063
        time_windows = [(t0-120/86400, t0+1000/86400)]
        ra = 288.338178
        dec = 19.771496
        fermi_path = data_dir.joinpath("SC00.fits")
        agile_path = "/ASDC_PROC2/DATA_2/INDEX/LOG.log.index"
        run = 50
        zmax = 80
        mode = "all"
        step = 1
        data_column_name = "rate"
        vertical_boxes_mjd = [t0, t0+200/86400]
        ap_agile = data_dir.joinpath("ALL_10s_emin100_emax10000_r5_DQ0_FOV70.ap.ap4")
        ap_fermi = data_dir.joinpath("lc_grb10sr5t0GRBconv.out")
        tstart = time_windows[0][0]
        tstop = time_windows[0][1]
        time_range=AstroUtils.time_mjd_to_agile_seconds(time_windows[0])
        trigger_time_tt = AstroUtils.time_mjd_to_agile_seconds(tstart)
        add_rm = True
        rm_files = [data_dir.joinpath("080412_RM-GRID_LC.txt"), data_dir.joinpath("080412_RM-AC0_LC.txt")]
        rm_labels = ['GRID', 'AC0']

        ageng = AGEngDisplayComparison()

       
        