# DESCRIPTION
#       Agilepy software
#
# NOTICE
#      Any information contained in this software
#      is property of the AGILE TEAM and is strictly
#      private and confidential.
#      Copyright (C) 2005-2020 AGILE Team.
#          Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
#          Panebianco Gabriele <gabriele.panebianco@inaf.it>
#          Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
#          Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
#          Addis Antonio <antonio.addis@inaf.it>
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

import numpy as np
import os
import pytest
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.time import Time
from pathlib import Path
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.api.AGVisibility import AGVisibility

@pytest.mark.visibility
class TestAGVisibility:

    @pytest.mark.testlogsdir("api/test_logs/vis_init")
    @pytest.mark.testconfig("api/conf/conf_visibility_3C454.3.yaml")
    def test_init(self, environ_test_logs_dir, config):
        """Test that the class is initialised and the mother class methods work."""

        # Test constructor
        ag_vis = AGVisibility(config)
        
        AGILE_DIR = os.environ['AGILE']
        testdata = Path(AGILE_DIR).joinpath("agilepy-test-data/test_dataset_agn/LOG/LOG.index")
        fermidata= Path(AGILE_DIR).joinpath("agilepy-test-data/visibility/Fermi_test_SC00.fits")
        
        # Test input data
        assert ag_vis.config.getSectionOfOption("logfile")=="input"
        assert ag_vis.config.getOptionValue("logfile") == str(testdata)
        assert ag_vis.getOption("logfile") == str(testdata)
        assert "$" not in ag_vis.getOption("logfile")
        assert str(environ_test_logs_dir) in ag_vis.getAnalysisDir()
        assert ag_vis.getOption("fermi_spacecraft_file") == str(fermidata)
        
        # Test Selection
        assert ag_vis.getOption("timetype") == "TT"
        assert ag_vis.getOption("step") == pytest.approx(30, rel=1e-6)
        assert ag_vis.getOption("tmin") == pytest.approx(104371200, rel=1e-6)
        assert ag_vis.getOption("tmax") == pytest.approx(632620800, rel=1e-6)
        
        # Test Source
        assert ag_vis.getOption("frame") == "icrs"
        assert ag_vis.getOption("coord1") is None
        assert ag_vis.getOption("coord2") is None
        
        # Test Attributes
        assert ag_vis.agileVisibility is None
        assert ag_vis.fermiVisibility is None
        
        # Test option setting with good and bad values
        ag_vis.setOptions(coord1=343.496, coord2=16.151, frame='icrs')
        ag_vis.setOptions(tmin=AstroUtils.convert_time_to_agile_seconds(Time(55513, format='mjd')),
                          tmax=AstroUtils.convert_time_to_agile_seconds(Time(55521, format='mjd')),
                          timetype="TT"
                          )
        
        assert ag_vis.getOption("tmin") == pytest.approx(216691200)
        assert ag_vis.getOption("tmax") == pytest.approx(217382400)
        assert ag_vis.getOption("coord1") == pytest.approx(343.496)
        assert ag_vis.getOption("coord2") == pytest.approx(16.151)



    @pytest.mark.testlogsdir("api/test_logs/vis_read")
    @pytest.mark.testconfig("api/conf/conf_visibility_3C454.3.yaml")
    @pytest.mark.testdatafile("api/data/visibility_agile_216691200_217382400.csv")
    def test_visibilityAnalysis(self, environ_test_logs_dir, config, testdata):
        """Test that the satellites' pointing directions are correctly read."""
        
        ag_vis = AGVisibility(config)
        ag_vis.setOptions(coord1=343.496, coord2=16.151, frame='icrs')
        ag_vis.setOptions(tmin=216691200, tmax=217382400, timetype="TT")
        
        # Get the AGILE and Fermi Tables
        agile_visibility_table = ag_vis.computePointingDirection(writeFiles=True)
        fermi_visibility_table = ag_vis.getFermiPointing(writeFiles=True)
        
        # Check values
        DataDirectory = Path(testdata).absolute().parent
        RefAgileTable = Table.read(testdata)
        RefFermiTable = Table.read(DataDirectory.joinpath("visibility_fermi_216691200_217382400.csv"))
        target = SkyCoord(343.496, 16.151, frame='icrs', unit='deg')
        
        # Assert AGILE
        assert len(RefAgileTable) == len(agile_visibility_table)
        assert np.max(np.abs(RefAgileTable['TT_start' ].data - agile_visibility_table['TT_start' ].data))<1E-3
        assert np.max(np.abs(RefAgileTable['TT_stop'  ].data - agile_visibility_table['TT_stop'  ].data))<1E-3
        assert np.max(np.abs(RefAgileTable['AGILE_RA' ].data - agile_visibility_table['AGILE_RA' ].data))<1E-3
        assert np.max(np.abs(RefAgileTable['AGILE_DEC'].data - agile_visibility_table['AGILE_DEC'].data))<1E-3
        pointings = SkyCoord(ra=agile_visibility_table['AGILE_RA'], dec=agile_visibility_table['AGILE_DEC'], frame="icrs", unit="deg")
        offsets = target.separation(pointings).to("deg").value
        assert np.max(np.abs(offsets - agile_visibility_table['offaxis_angle_deg'].data))<1E-3
        
        # Assert step is 30s as set
        times = RefAgileTable['TT_start'].data
        #diffs = times[1:]-times[:-1] # Fails if there is any lack of data
        diffs = np.array([times[1]-times[0]])
        assert np.max(np.abs(diffs - 30.0))<1
        
        # Assert Fermi
        assert len(RefFermiTable) == len(fermi_visibility_table)
        assert np.max(np.abs(RefFermiTable['TT_start' ].data - fermi_visibility_table['TT_start' ].data))<1E-3
        assert np.max(np.abs(RefFermiTable['TT_stop'  ].data - fermi_visibility_table['TT_stop'  ].data))<1E-3
        assert np.max(np.abs(RefFermiTable['MJD_start'].data - fermi_visibility_table['MJD_start'].data))<1E-3
        assert np.max(np.abs(RefFermiTable['MJD_stop' ].data - fermi_visibility_table['MJD_stop' ].data))<1E-3
        assert np.max(np.abs(RefFermiTable['MET_START'].data - fermi_visibility_table['MET_START'].data))<1E-3
        assert np.max(np.abs(RefFermiTable['MET_STOP' ].data - fermi_visibility_table['MET_STOP' ].data))<1E-3
        assert np.max(np.abs(RefFermiTable['RA_SCZ'   ].data - fermi_visibility_table['RA_SCZ'   ].data))<1E-3
        assert np.max(np.abs(RefFermiTable['DEC_SCZ'  ].data - fermi_visibility_table['DEC_SCZ'  ].data))<1E-3
        pointings = SkyCoord(ra=fermi_visibility_table['RA_SCZ'], dec=fermi_visibility_table['DEC_SCZ'], frame="icrs", unit="deg")
        offsets = target.separation(pointings).to("deg").value
        assert np.max(np.abs(offsets - fermi_visibility_table['offaxis_angle_deg'].data))<1E-3
        
        # Plot production
        plots = ag_vis.plotVisibility(
            mjd_limits=(55519, 55519.5), maxOffaxis=60,
            plotFermi=True, plotHistogram=True, saveImages=True,
            showPositionPanels=True
        )
        assert len(plots)==2
        for plot in plots:
            assert os.path.isfile(plot)

