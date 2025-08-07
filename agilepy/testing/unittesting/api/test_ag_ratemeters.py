import pytest
import numpy as np
import os

from astropy.table import Table

from agilepy.api.AGRatemeters import AGRatemeters
from agilepy.utils.AstroUtils import AstroUtils

@pytest.mark.ratemeters
class TestAGRatemeters:
    
    @pytest.mark.testlogsdir("api/test_logs/rm_init")
    @pytest.mark.testconfig("api/conf/agilepyconf_ratemeters.yaml")
    @pytest.mark.testdatafile("api/data/PKP080686_1_3913_000.lv1.cor.gz")
    def test_init(self, environ_test_logs_dir, config, testdata):
        """Test that the class is initialised and the mother class methods work."""

        # Test constructor
        ag_rm = AGRatemeters(config)
        
        assert str(environ_test_logs_dir) in ag_rm.getAnalysisDir()
        ag_rm.printOptions()
        assert ag_rm.getOption("file_path") == testdata
        assert ag_rm.getOption("timetype") == "TT"
        assert ag_rm.getOption("T0") == pytest.approx(594047787, rel=1e-6)
        assert ag_rm.getOption("background_tmin") == pytest.approx(-100.0, rel=1e-6)
        assert ag_rm.getOption("background_tmax") == pytest.approx(-90.0, rel=1e-6)
        assert ag_rm.getOption("signal_tmin") == pytest.approx(-1.0, rel=1e-6)
        assert ag_rm.getOption("signal_tmax") == pytest.approx(3.0, rel=1e-6)
        
        ag_rm.setOptions(signal_tmin=-2.0)
        assert ag_rm.getOption("signal_tmin") == pytest.approx(-2.0)
        
        assert ag_rm.ratemeters_tables is None


    @pytest.mark.testlogsdir("api/test_logs/rm_read")
    @pytest.mark.testconfig("api/conf/agilepyconf_ratemeters.yaml")
    @pytest.mark.testdatafile("api/data/PKP080686_1_3913_000.lv1.cor.gz")
    def test_read_ratemeters(self, environ_test_logs_dir, config, testdata):
        """Test that the ratemeters are correctly read."""
        
        # Define Object
        ag_rm = AGRatemeters(config)
        assert ag_rm.ratemeters_tables is None
        
        # Run Function
        ratemeters_tables = ag_rm.read_ratemeters()
                
        # Assert files are written
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-GRID_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-SA_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-MCAL_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC0_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC1_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC2_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC3_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC4_LC.txt")
        
        # Assert results


