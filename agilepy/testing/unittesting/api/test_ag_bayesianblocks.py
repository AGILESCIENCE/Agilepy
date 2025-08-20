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
import numpy as np
import os

from astropy.table import Table

from agilepy.api.AGBayesianBlocks import AGBayesianBlocks


@pytest.mark.bayesianblocks
class TestAGBayesianBlocks():

    @pytest.mark.testlogsdir("api/test_logs/bb_init")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_init(self, environ_test_logs_dir, config, testdata):
        """Test that the class is initialised and the mother class methods work."""

        ag_bb = AGBayesianBlocks(config)
        
        assert str(environ_test_logs_dir) in ag_bb.getAnalysisDir()
        ag_bb.printOptions()
        assert ag_bb.getOption("file_path") == testdata
        assert ag_bb.getOption("file_mode") == "AGILE_AP"
        ag_bb.setOptions(tstart=55510, tstop=55530)
        assert ag_bb.getOption("tstart")==55510
        assert ag_bb.getOption("tstop" )==55530
    
    
    
    @pytest.mark.testlogsdir("api/test_logs/bb_select")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_select_events(self, environ_test_logs_dir, config, testdata):
        """Test the select events method."""
        # Define Object
        ag_bb = AGBayesianBlocks(config)
        
        # Data not selected yet
        assert ag_bb.getDataIn() == {}
        assert ag_bb.datamode == None
        
        ### Select events
        ag_bb.selectEvents() # No arguments -> Taken from the configuration
        
        # Check that the events are correctly read
        events_selected = ag_bb.getDataIn()
        
        data_table = Table.read(testdata,format="ascii", names=["TT_start","TT_stop","exposure","on_counts"])
        
        assert ag_bb.datamode == 2
        assert ag_bb.filemode == 2
        assert len(events_selected['x']) == 65
        assert len(events_selected['t']) == 65
        assert len(events_selected['sigma']) == 65
        assert events_selected['dt'] == 86400
        assert events_selected['datamode'] == 2
        assert np.allclose(events_selected['t_delta'], np.array(65*[86400]), rtol=1e-3, atol=1e-5)
        assert np.allclose(events_selected['cts'    ], data_table['on_counts'].data, rtol=1e-3, atol=1e-5)
        assert np.allclose(events_selected['exp'    ], data_table['exposure' ].data, rtol=1e-3, atol=1e-5)
        assert len(events_selected['data_cells'])==66
        assert np.allclose(events_selected['data_cells'], np.append(data_table['TT_start'].data, data_table['TT_stop'][-1]), rtol=1e-3, atol=1e-5)
        assert len(events_selected['rate'])==65
        
        # Head event method
        headEvents = ag_bb.headEvents()
        assert len(headEvents)==5
        
        # Blocks not selected yet
        assert ag_bb.getDataOut() == {}
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=False, saveImage=False, plotBayesianBlocks=False, plotRate=False, plotDataCells=False)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=False, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_data.png"
        assert os.path.isfile(plot_file)
        
        # rate must not be produced, as it requires bayesian blocks
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=False, plotRate=True, plotDataCells=False)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_data_rate.png"
        assert not os.path.isfile(plot_file)
    
    
    @pytest.mark.testlogsdir("api/test_logs/bb_select_args")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_select_events_args(self, environ_test_logs_dir, config, testdata):
        """Test the select events method."""
        # Define Object
        ag_bb = AGBayesianBlocks(config)
        
        # Data not selected yet
        assert ag_bb.getDataIn() == {}
        assert ag_bb.datamode is None
        
        ### Select events
        ag_bb.selectEvents(tstart=55500, tstop=55550) # Change arguments
        events_selected = ag_bb.getDataIn()
                
        assert ag_bb.datamode == 2
        assert ag_bb.filemode == 2
        
        assert len(events_selected['x']) == 50
        assert len(events_selected['t']) == 50
        assert len(events_selected['sigma']) == 50
        assert events_selected['dt'] == 86400
        assert events_selected['datamode'] == 2
        assert np.allclose(events_selected['t_delta'], np.array(50*[86400]), rtol=1e-3, atol=1e-5)
        assert len(events_selected['data_cells'])==51
        assert len(events_selected['rate'])==50
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=False, saveImage=False, plotBayesianBlocks=False)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_data.png"
        assert os.path.isfile(plot_file)
        
            
    
    @pytest.mark.testlogsdir("api/test_logs/bb_execute")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_bayesian_blocks(self, environ_test_logs_dir, config, testdata):
        """Test the bayesian blocks method."""
        
        ag_bb = AGBayesianBlocks(config)
        ag_bb.selectEvents()
        assert ag_bb.getDataOut() == {} # Blocks not selected yet
        
        # Compute Bayesian Blocks
        ag_bb.bayesianBlocks() # No arguments -> Taken from the configuration
        
        blocks_computed = ag_bb.getDataOut()
        #print(blocks_computed)

        assert blocks_computed['ncp_prior'] == pytest.approx(1.05, rel=1e-3)
        assert len(blocks_computed['data_cells'])== 66
        assert blocks_computed['N'           ] == 65
        assert blocks_computed['N_data_cells'] == 65
        assert len(blocks_computed['edge_vec'])== 7
        assert blocks_computed['N_change_points'  ]  == 16
        assert len(blocks_computed['change_points']) == 16
        assert len(blocks_computed['edge_points'  ]) == 16
        assert len(blocks_computed['sum_blocks'   ]) == 17
        assert len(blocks_computed['mean_blocks'  ]) == 17
        assert len(blocks_computed['dt_event_vec' ]) == 17
        assert len(blocks_computed['dt_block_vec' ]) == 17
        assert len(blocks_computed['blockrate'    ]) == 17
        assert len(blocks_computed['blockrate2'   ]) == 17
        assert len(blocks_computed['eventrate'    ]) == 17
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=False, saveImage=False, plotBayesianBlocks=False)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results.png"
        assert os.path.isfile(plot_file)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
        

    @pytest.mark.testlogsdir("api/test_logs/bb_exe_args")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_bayesian_blocks_args(self, environ_test_logs_dir, config, testdata):
        """Test the bayesian blocks method."""
        
        ag_bb = AGBayesianBlocks(config)
        ag_bb.selectEvents()
        ag_bb.bayesianBlocks(gamma=0.45, useerror=False)
        
        blocks_computed = ag_bb.getDataOut()
        #print(blocks_computed)

        assert blocks_computed['ncp_prior'] == pytest.approx(0.799, rel=1e-3)
        assert len(blocks_computed['data_cells'])== 66
        assert blocks_computed['N'           ] == 65
        assert blocks_computed['N_data_cells'] == 65
        assert len(blocks_computed['edge_vec'])== 7
        assert blocks_computed['N_change_points'  ]  == 18
        assert len(blocks_computed['change_points']) == 18
        assert len(blocks_computed['edge_points'  ]) == 18
        assert len(blocks_computed['sum_blocks'   ]) == 19
        assert len(blocks_computed['mean_blocks'  ]) == 19
        assert len(blocks_computed['dt_event_vec' ]) == 19
        assert len(blocks_computed['dt_block_vec' ]) == 19
        assert len(blocks_computed['blockrate'    ]) == 19
        assert len(blocks_computed['blockrate2'   ]) == 19
        assert len(blocks_computed['eventrate'    ]) == 19
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=False, saveImage=False, plotBayesianBlocks=False)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results.png"
        assert os.path.isfile(plot_file)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
        
        
    @pytest.mark.testlogsdir("api/test_logs/bb_ap_alt1")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_bb_ap_alternative1(self, environ_test_logs_dir, config, testdata):
        """Test the bayesian blocks method with ratecorrection=None."""
        
        ag_bb = AGBayesianBlocks(config)
        ag_bb.selectEvents(ratecorrection=None)
        with pytest.raises(ValueError):
            # Regular events must have only 0 and 1 in x
            ag_bb.bayesianBlocks(fitness="regular_events")
        
        # Use fitness Events
        ag_bb.bayesianBlocks()
        blocks_computed = ag_bb.getDataOut()
        #print(blocks_computed)

        assert blocks_computed['ncp_prior'] == pytest.approx(1.049, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 65
        assert len(blocks_computed['edge_vec'])== 7
        assert blocks_computed['N_change_points'] == 16
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
    
    
    @pytest.mark.testlogsdir("api/test_logs/bb_ap_alt2")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_bb_ap_alternative2(self, environ_test_logs_dir, config, testdata):
        """Test the bayesian blocks method with ratecorrection=-1."""
        
        ag_bb = AGBayesianBlocks(config)
        ag_bb.selectEvents(ratecorrection=-1)
        ag_bb.bayesianBlocks()
        blocks_computed = ag_bb.getDataOut()
        #print(blocks_computed)

        assert blocks_computed['ncp_prior'] == pytest.approx(1.049, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 65
        assert len(blocks_computed['edge_vec'])== 7
        assert blocks_computed['N_change_points'] == 18
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
        
        
    @pytest.mark.testlogsdir("api/test_logs/bb_ap_alt3")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_bb_ap_alternative3(self, environ_test_logs_dir, config, testdata):
        """Test the bayesian blocks method with ratecorrection=float."""
        
        ag_bb = AGBayesianBlocks(config)
        ag_bb.selectEvents(ratecorrection=3.0E7)
        ag_bb.bayesianBlocks()
        blocks_computed = ag_bb.getDataOut()
        #print(blocks_computed)

        assert blocks_computed['ncp_prior'] == pytest.approx(1.049, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 65
        assert len(blocks_computed['edge_vec'])== 5
        assert blocks_computed['N_change_points'] == 40
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
        

    @pytest.mark.testlogsdir("api/test_logs/bb_ap_alt4")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_bb_ap_alternative4(self, environ_test_logs_dir, config, testdata):
        """Test the bayesian blocks method with fitness=measures."""
        
        ag_bb = AGBayesianBlocks(config)
        ag_bb.selectEvents(ratecorrection=0)
        ag_bb.bayesianBlocks(fitness="measures")
        blocks_computed = ag_bb.getDataOut()

        assert blocks_computed['ncp_prior'] == pytest.approx(1.049, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 65
        assert len(blocks_computed['edge_vec'])== 7
        assert blocks_computed['N_change_points'] == 16
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
        

    @pytest.mark.testlogsdir("api/test_logs/bb_getconf")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_get_configuration(self, environ_test_logs_dir, testdata):
        """Test the creation of a configuration file."""
        
        confFilePath = os.environ['TEST_LOGS_DIR'] + "/conf.yaml"
        # Cleanup
        if os.path.isfile(confFilePath):
            os.remove(confFilePath)
        assert not os.path.isfile(confFilePath)
        AGBayesianBlocks.getConfiguration(confFilePath=confFilePath, outputDir=os.environ['TEST_LOGS_DIR'],
                                          filePath=testdata, fileMode="AGILE_AP",
                                          )
        assert os.path.isfile(confFilePath)
        
        ag_bb = AGBayesianBlocks(confFilePath)
        assert ag_bb.getOption("username") == "my_name"
        assert ag_bb.getOption("sourcename") == "bb-source"
        assert ag_bb.getOption("filenameprefix") == "analysis_product"
        assert ag_bb.getOption("logfilenameprefix") =="analysis_log"
        assert ag_bb.getOption("verboselvl") == 0
        
        assert ag_bb.getOption('file_path') == testdata
        assert ag_bb.getOption('file_mode') == "AGILE_AP"
        assert ag_bb.getOption('ratecorrection') == 0
        assert ag_bb.getOption('tstart') == None
        assert ag_bb.getOption('tstop' ) == None
        
        assert ag_bb.getOption('fitness' ) == "events"
        assert ag_bb.getOption('useerror') == True
        assert ag_bb.getOption('gamma'   ) == 0.35
        assert ag_bb.getOption('p0'      ) == None
        
    @pytest.mark.testlogsdir("api/test_logs/bb_mle")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s_lc_mle.txt")
    def test_bb_mle(self, environ_test_logs_dir, config, testdata):
        """Test the computation of Bayesian Blocks with a MLE file."""
        
        ag_bb = AGBayesianBlocks(config)
        ag_bb.setOptions(file_path=testdata, file_mode="AGILE_MLE")
        
        ag_bb.selectEvents()
        assert ag_bb.datamode == 2
        assert ag_bb.filemode == 3
        ag_bb.bayesianBlocks()
        
        # Plot
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
        
        # Asserts
        blocks_computed = ag_bb.getDataOut()
        assert blocks_computed['ncp_prior'] == pytest.approx(1.05, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 20
        assert len(blocks_computed['edge_vec'])== 5
        assert blocks_computed['N_change_points'] == 8
        

    @pytest.mark.testlogsdir("api/test_logs/bb_mle_alt")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s_lc_mle.txt")
    def test_bb_mle_alternative(self, environ_test_logs_dir, config, testdata):
        "Test MLE with ratecorrection values different than 0."
        
        # Rate Correction = None
        ag_bb = AGBayesianBlocks(config)
        ag_bb.setOptions(file_path=testdata, file_mode="AGILE_MLE", ratecorrection=None)
        ag_bb.selectEvents()
        assert ag_bb.datamode == 2
        assert ag_bb.filemode == 3
        ag_bb.bayesianBlocks()
        blocks_computed = ag_bb.getDataOut()
        assert blocks_computed['ncp_prior'] == pytest.approx(1.05, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 20
        assert len(blocks_computed['edge_vec'])== 4
        assert blocks_computed['N_change_points'] == 8
        
        # Rate Correction = -1
        ag_bb2 = AGBayesianBlocks(config)
        ag_bb2.setOptions(file_path=testdata, file_mode="AGILE_MLE", ratecorrection=-1)
        ag_bb2.selectEvents()
        ag_bb2.bayesianBlocks()
        assert ag_bb2.datamode == 2
        assert ag_bb2.filemode == 3
        assert blocks_computed['ncp_prior'] == pytest.approx(1.05, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 20
        assert len(blocks_computed['edge_vec'])== 4
        assert blocks_computed['N_change_points'] == 8
        
        # Rate Correction = 5E7
        ag_bb3 = AGBayesianBlocks(config)
        ag_bb3.setOptions(file_path=testdata, file_mode="AGILE_MLE", ratecorrection=5.0E7)
        ag_bb3.selectEvents()
        ag_bb3.bayesianBlocks()
        assert ag_bb3.datamode == 2
        assert ag_bb3.filemode == 3
        assert blocks_computed['ncp_prior'] == pytest.approx(1.05, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 20
        assert len(blocks_computed['edge_vec'])== 4
        assert blocks_computed['N_change_points'] == 8
    
    
    
    @pytest.mark.testlogsdir("api/test_logs/bb_custom")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s_lc_custom.txt")
    def test_bb_custom(self, environ_test_logs_dir, config, testdata):
        """Test the computation of Bayesian Blocks with a CUSTOM_LC file."""
        
        ag_bb = AGBayesianBlocks(config)
        ag_bb.setOptions(file_path=testdata, file_mode="CUSTOM_LC", tstart=None, tstop=None)
        
        ag_bb.selectEvents()
        assert ag_bb.datamode == 2
        assert ag_bb.filemode == 4
        ag_bb.bayesianBlocks()
        
        # Plot
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
        
        # Asserts
        blocks_computed = ag_bb.getDataOut()
        assert blocks_computed['ncp_prior'] == pytest.approx(1.05, rel=1e-3)
        assert blocks_computed['N_data_cells'] == 20
        assert len(blocks_computed['edge_vec'])== 10
        assert blocks_computed['N_change_points'] == 2


    @pytest.mark.testlogsdir("api/test_logs/bb_cus_alt")
    @pytest.mark.testconfig("config/conf/conf_bb.yaml")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s_lc_custom.txt")
    def test_bb_custom_alternative(self, environ_test_logs_dir, config, testdata):
        "Test CUSTOM with ratecorrection values different than 0."
        
        # Rate Correction = None
        ag_bb = AGBayesianBlocks(config)
        ag_bb.setOptions(file_path=testdata, file_mode="CUSTOM_LC", ratecorrection=None, tstart=None, tstop=None)
        ag_bb.selectEvents()
        assert ag_bb.datamode == 2
        assert ag_bb.filemode == 4
        ag_bb.bayesianBlocks()
        blocks_computed = ag_bb.getDataOut()
        assert blocks_computed['N_data_cells'] == 20
        assert len(blocks_computed['edge_vec'])== 2
        assert blocks_computed['N_change_points'] == 17
        
        # Rate Correction = -1
        ag_bb2 = AGBayesianBlocks(config)
        ag_bb2.setOptions(file_path=testdata, file_mode="CUSTOM_LC", ratecorrection=-1, tstart=None, tstop=None)
        ag_bb2.selectEvents()
        ag_bb2.bayesianBlocks()
        assert ag_bb2.datamode == 2
        assert ag_bb2.filemode == 4
        assert blocks_computed['N_data_cells'] == 20
        assert len(blocks_computed['edge_vec'])== 2
        assert blocks_computed['N_change_points'] == 17
        
        # Rate Correction = 0.5
        ag_bb3 = AGBayesianBlocks(config)
        ag_bb3.setOptions(file_path=testdata, file_mode="CUSTOM_LC", ratecorrection=0.5, tstart=None, tstop=None)
        ag_bb3.selectEvents()
        ag_bb3.bayesianBlocks()
        assert ag_bb3.datamode == 2
        assert ag_bb3.filemode == 4
        assert blocks_computed['N_data_cells'] == 20
        assert len(blocks_computed['edge_vec'])== 2
        assert blocks_computed['N_change_points'] == 17

    
    @pytest.mark.testlogsdir("api/test_logs/bb_ph")
    @pytest.mark.testconfig("api/conf/conf_bb_agile_ph.yaml")
    @pytest.mark.testdatafile("api/data/test_data.ph")
    def test_bb_ph(self, environ_test_logs_dir, config, testdata):
       """Test the computation of Bayesian Blocks with a AGILE_PH file."""
       
       ag_bb = AGBayesianBlocks(config)
       ag_bb.setOptions(file_path=testdata)
       
       ag_bb.selectEvents()
       events_selected = ag_bb.getDataIn()
       assert ag_bb.datamode == 1
       assert ag_bb.filemode == 1
       
       assert len(events_selected['x']) == 1285
       assert len(events_selected['t']) == 1285
       assert len(events_selected['sigma']) == 1285
       assert events_selected['dt'] == 0
       assert events_selected['datamode'] == 1
       
       # Run Bayesian Blocks
       ag_bb.bayesianBlocks()
       
       # Asserts
       blocks_computed = ag_bb.getDataOut()
       print(blocks_computed)
       assert blocks_computed['ncp_prior'] == pytest.approx(3.817, rel=1e-3)
       assert blocks_computed['N_data_cells'] == 1285
       assert len(blocks_computed['edge_vec'])== 307
       assert blocks_computed['N_change_points'] == 2
       
       # Plot
       ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True, plotDataCells=False, plotSumBlocks=True)
       plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
       assert os.path.isfile(plot_file)
