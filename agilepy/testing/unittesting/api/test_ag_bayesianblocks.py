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
from pathlib import Path

from agilepy.api.AGBayesianBlocks import AGBayesianBlocks
from agilepy.core.CustomExceptions import ConfigurationsNotValidError, ConfigFileOptionTypeError, OptionNotFoundInConfigFileError, CannotSetNotUpdatableOptionError, AnalysisClassNotSupported, DeprecatedOptionError


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
        assert ag_bb.getOption("ap_path") == testdata
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
        assert ag_bb.datamode is None
        
        ### Select events
        ag_bb.selectEvents() # No arguments -> Taken from the configuration
        
        # Check that the events are correctly read
        events_selected = ag_bb.getDataIn()
        
        data_table = Table.read(testdata,format="ascii", names=["TT_start","TT_stop","exposure","on_counts"])
        
        assert ag_bb.datamode == 2
        
        assert len(ag_bb.sigma)==65
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
        ag_bb.plotBayesianBlocks(plotYErr=False, saveImage=False, plotBayesianBlocks=False)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_data.png"
        assert os.path.isfile(plot_file)
        
        # rate must not be produced, as it requires bayesian blocks
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=False, plotRate=True, plotDataCells=True)
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
        assert ag_bb.sigma is not None

        assert blocks_computed['ncp_prior'] == pytest.approx(1.05, rel=1e-3)        
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
        assert blocks_computed['N_change_points'  ]  == 22
        assert len(blocks_computed['change_points']) == 22
        assert len(blocks_computed['edge_points'  ]) == 22
        assert len(blocks_computed['sum_blocks'   ]) == 23
        assert len(blocks_computed['mean_blocks'  ]) == 23
        assert len(blocks_computed['dt_event_vec' ]) == 23
        assert len(blocks_computed['dt_block_vec' ]) == 23
        assert len(blocks_computed['blockrate'    ]) == 23
        assert len(blocks_computed['blockrate2'   ]) == 23
        assert len(blocks_computed['eventrate'    ]) == 23
        
        # Make plot
        ag_bb.plotBayesianBlocks(plotYErr=False, saveImage=False, plotBayesianBlocks=False)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results.png"
        assert os.path.isfile(plot_file)
        
        ag_bb.plotBayesianBlocks(plotYErr=True, saveImage=True, plotBayesianBlocks=True, plotRate=True, plotDataCells=True)
        plot_file = ag_bb.getAnalysisDir()+"/plots/bayesianblocks_results_rate.png"
        assert os.path.isfile(plot_file)
        
        
    @pytest.mark.testlogsdir("api/test_logs/bb_getconf")
    @pytest.mark.testdatafile("api/data/3C454.3_2010flare_86400s.ap")
    def test_get_configuration(self, environ_test_logs_dir, testdata):
        
        confFilePath = os.environ['TEST_LOGS_DIR'] + "/conf.yaml"
        # Cleanup
        if os.path.isfile(confFilePath):
            os.remove(confFilePath)
        assert not os.path.isfile(confFilePath)
        AGBayesianBlocks.getConfiguration(confFilePath=confFilePath,
                                          outputDir=os.environ['TEST_LOGS_DIR'],
                                          ap_path=testdata
                                          )
        assert os.path.isfile(confFilePath)
        
        ag_bb = AGBayesianBlocks(confFilePath)
        assert ag_bb.getOption("username") == "my_name"
        assert ag_bb.getOption("sourcename") == "bb-source"
        assert ag_bb.getOption("filenameprefix") == "analysis_product"
        assert ag_bb.getOption("logfilenameprefix") =="analysis_log"
        assert ag_bb.getOption("verboselvl") == 0
        
        assert ag_bb.getOption('ap_path'   ) == testdata
        assert ag_bb.getOption('mle_path'  ) == None
        assert ag_bb.getOption('ph_path'   ) == None
        assert ag_bb.getOption('rate_path' ) == None
        assert ag_bb.getOption('rate'      ) == False
        assert ag_bb.getOption('ratefactor') == 0
        assert ag_bb.getOption('csv_detections_path') == None
        assert ag_bb.getOption('event_id') == None
        assert ag_bb.getOption('tstart'  ) == None
        assert ag_bb.getOption('tstop'   ) == None
        
        assert ag_bb.getOption('fitness' ) == "events"
        assert ag_bb.getOption('useerror') == True
        assert ag_bb.getOption('gamma'   ) == 0.35
        assert ag_bb.getOption('p0'      ) == None
        
        
        
    #TODO: test mle_path, ph_path, rate_path, detections_csv_path
