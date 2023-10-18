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
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.api.AGEngDisplayComparison import AGEngDisplayComparison
from agilepy.api.AGEngAgileFermiOffAxisVisibilityComparison import AGEngAgileFermiOffAxisVisibilityComparison
class TestAGEngDisplayComparison:

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

    @pytest.fixture
    def data_dir(self):
        currentDirPath = Path(__file__).parent.absolute()
        return currentDirPath.joinpath("data/test_ag_eng_agile_fermi_offaxis_visibility_comparison")

    @pytest.mark.skip(reason="This test needs to access to /ASDC_PROC2/DATA_2/INDEX/LOG.log.index")        
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

    
    @pytest.mark.skip(reason="This test needs to access to /ASDC_PROC2/DATA_2/INDEX/LOG.log.index")        
    def test_plot_agile_fermi_comparison_tt(self, data_dir, conf):
        # params for AGEngAgileFermiOffAxisVisibilityComparison()
        t0_mjd = 59861.55346063
        time_windows = [(t0_mjd-120/86400, t0_mjd+1000/86400)]
        ra = 288.338178
        dec = 19.771496
        run = 50
        zmax = 80
        mode = "all"
        step = 1
        fermi_path = data_dir.joinpath("SC00.fits")
        agile_path = "/ASDC_PROC2/DATA_2/INDEX/LOG.log.index"
        # get offaxis path by runnig visibilityPlot()
        vis = AGEngAgileFermiOffAxisVisibilityComparison(conf)
        offaxis_path = vis.visibilityPlot(time_windows, ra, dec, str(fermi_path), str(agile_path), run, zmax, mode, step)[0]

        # params for AGEngDisplayComparison()
        t0_tt = AstroUtils.time_mjd_to_agile_seconds(t0_mjd)
        agile_datainfo = {'label': 'AGILE', 'column': 'cts', 'error_column': None}
        fermi_datainfo = {'label': 'AGILE', 'column': 'cts', 'error_column': None}        
        agile_time_windows = [t0_tt, t0_tt+200]
        ap_agile = data_dir.joinpath("ALL_10s_emin100_emax10000_r5_DQ0_FOV70.ap.ap4")
        ap_fermi = data_dir.joinpath("lc_grb10sr5t0GRBconv.out")
        timerange = [t0_tt-120, t0_tt+1000]
        add_rm = True
        rm_files = [data_dir.joinpath("080412_RM-GRID_LC.txt"), data_dir.joinpath("080412_RM-AC0_LC.txt")]
        rm_labels = ['GRID', 'AC0']

        # test
        ageng = AGEngDisplayComparison(logger=vis.logger)
        ageng.plot_agile_fermi_comparison(agile_data_file=ap_agile, fermi_data_file=ap_fermi, offaxis_path=offaxis_path, timetype="TT", timerange=timerange, agile_time_windows=agile_time_windows, zmax=zmax,  trigger_time_tt=t0_tt, add_rm=add_rm, rm_files=rm_files, rm_labels=rm_labels, agile_datainfo=agile_datainfo, fermi_datainfo=fermi_datainfo, add_stats_lines=True)

       
        