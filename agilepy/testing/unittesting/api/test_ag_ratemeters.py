import pytest
import numpy as np
import os

from astropy.table import Table
from pathlib import Path

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
        
        ag_rm.setOptions(signal_tmin=-2.0, signal_tmax=4.0)
        assert ag_rm.getOption("signal_tmin") == pytest.approx(-2.0, rel=1e-6)
        assert ag_rm.getOption("signal_tmax") == pytest.approx( 4.0, rel=1e-6)
        
        assert ag_rm.ratemetersTables is None


    @pytest.mark.testlogsdir("api/test_logs/rm_read")
    @pytest.mark.testconfig("api/conf/agilepyconf_ratemeters.yaml")
    @pytest.mark.testdatafile("api/data/PKP080686_1_3913_000.lv1.cor.gz")
    def test_readRatemeters_plotRatemeters(self, environ_test_logs_dir, config, testdata):
        """Test that the ratemeters are correctly read."""
        # Define Object
        ag_rm = AGRatemeters(config)
        assert ag_rm.ratemetersTables is None
        # Run Function
        ratemetersTables = ag_rm.readRatemeters()
        
        ####################
        # Assert files are written
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-GRID_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-SA_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-MCAL_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC0_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC1_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC2_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC3_LC.txt")
        assert os.path.isfile(ag_rm.getAnalysisDir()+"/rm/RM-AC4_LC.txt")
        
        # Check results value using the AC Top Table
        ResTable = ratemetersTables['AC0']
        
        DataDirectory = Path(testdata).absolute().parent
        DataTable = Table.read(DataDirectory.joinpath("GRB221028A_RM-AC0_LC.txt"), format="ascii")
        
        assert np.max(np.abs(DataTable['OBT']-ResTable['OBT'])) < 1e-6
        assert np.max(np.abs(DataTable['COUNTS']-ResTable['COUNTS'])) < 1e-6
        assert np.max(np.abs(DataTable['COUNTS_D']-ResTable['COUNTS_D'])) < 1e-6
        ####################
        
        
        ####################
        # Test Plot Function
        plots = ag_rm.plotRatemeters(plotInstruments=["2RM","3RM","8RM","AC0","AC1","AC2","AC3","AC4","MCAL","GRID","SA"],
                                     plotRange=(-100,100),
                                     useDetrendedData=True
                                     )
        plots+= ag_rm.plotRatemeters(plotInstruments=["AC0"] ,plotRange=(-100,100),useDetrendedData=False)
        plots+= ag_rm.plotRatemeters(plotInstruments=["MCAL"],plotRange=(-100,100),useDetrendedData=False)
        for plot in plots:
            assert os.path.isfile(plot)
        assert len(plots)==6
        
        with pytest.raises(KeyError):
            ag_rm.plotRatemeters(plotInstruments=["Fake"])
        ####################
        
        
        ####################
        # Test Aperture Photometry Analysis
        detrended_AP = ag_rm.analyseSignal(useDetrendedData=True)
        detrended_data = Table.read(DataDirectory.joinpath("GRB221028A_analysis_D.csv"))
        assert np.max(np.abs(detrended_AP['N_ON']-detrended_data['N_ON'])) < 1e-6
        assert np.max(np.abs(detrended_AP['t_ON']-detrended_data['t_ON'])) < 1e-6
        assert np.max(np.abs(detrended_AP['N_OFF']-detrended_data['N_OFF'])) < 1e-6
        assert np.max(np.abs(detrended_AP['t_OFF']-detrended_data['t_OFF'])) < 1e-6
        
        raw_AP = ag_rm.analyseSignal(useDetrendedData=False)
        raw_data = Table.read(DataDirectory.joinpath("GRB221028A_analysis_ND.csv"))
        assert np.max(np.abs(raw_AP['N_ON']-raw_data['N_ON'])) < 1e-6
        assert np.max(np.abs(raw_AP['t_ON']-raw_data['t_ON'])) < 1e-6
        assert np.max(np.abs(raw_AP['N_OFF']-raw_data['N_OFF'])) < 1e-6
        assert np.max(np.abs(raw_AP['t_OFF']-raw_data['t_OFF'])) < 1e-6
        ####################