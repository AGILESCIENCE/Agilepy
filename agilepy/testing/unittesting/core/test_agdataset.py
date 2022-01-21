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
from cgi import test
import os
from shutil import rmtree
import pytest
from pathlib import Path
from agilepy.core.AGDataset import AGDataset 
from agilepy.core.AGDataset import DataStatus
from agilepy.config.AgilepyConfig import AgilepyConfig

class TestAGDataset:


    @pytest.mark.testdir("core")
    def test_download_data(self, logger):

        

        testOutputDir = Path( __file__ ).absolute().parent.joinpath("test_out")

        if testOutputDir.exists():
            rmtree(str(testOutputDir))
        
        testOutputDir.mkdir(exist_ok=True, parents=True)

        queryEVTPath = testOutputDir.joinpath("EVT.qfile")
        queryLOGPath = testOutputDir.joinpath("LOG.qfile")

        with open(queryEVTPath, "w") as inf:
            inf.write("""2020-01-15T00:00:00 2020-01-31T00:00:00
2020-03-15T00:00:00 2020-03-31T00:00:00""")
        with open(queryLOGPath, "w") as infLOG:
            infLOG.write("""2020-01-15T00:00:00 2020-01-31T00:00:00
2020-03-15T00:00:00 2020-03-31T00:00:00""")

        os.environ["TEST_LOGS_DIR"] = str(Path( __file__ ).absolute().parent.joinpath("test_out"))

        configPath = Path( __file__ ).absolute().parent.joinpath("test_data", "test_download_data_config.yaml")
        config = AgilepyConfig()
        config.loadBaseConfigurations(configPath)

        agdataset = AGDataset(logger)

        tmin = 57083 # 2015-02-28T00:00:00
        tmax = 57090 # 2015-03-15T00:00:00
        downloaded = agdataset.downloadData(config, tmin, tmax)

        assert downloaded == True

    @pytest.mark.testdir("core")
    def test_extract_data_evt(self, logger):

        queryEVTPath = Path( __file__ ).absolute().parent.joinpath("test_data", "test_extract_data_EVT.qfile")

        agdataset = AGDataset(logger)
        blocksize = 15

        # Test 1 - boundaries
        # =================
        # ^               ^
        tmin = 57081 # 2015-02-28T00:00:00
        tmax = 57096 # 2015-03-15T00:00:00
        assert DataStatus.OK == agdataset.dataIsAlreadyPresent(tmin, tmax, queryEVTPath, blocksize)

        # Test 2 - inside range
        # =================
        #   ^          ^   
        tmin = 57082 # 2015-03-01T00:00:00
        tmax = 57086 # 2015-03-05T00:00:00
        assert DataStatus.OK == agdataset.dataIsAlreadyPresent(tmin, tmax, queryEVTPath, blocksize)

        # Test 2 - boundaries of multiple lines
        # =================
        # ^
        # =================
        #                 ^          
        tmin = 59000 # 2020-05-31T00:00:00
        tmax = 59030 # 2020-06-30T00:00:00
        assert DataStatus.OK == agdataset.dataIsAlreadyPresent(tmin, tmax, queryEVTPath, blocksize)

        # Test 3 - inside of multiple lines
        # =================
        #   ^
        # =================
        #               ^          
        tmin = 59014 # 2020-06-14T00:00:00
        tmax = 59028 # 2020-06-28T00:00:00
        assert DataStatus.OK == agdataset.dataIsAlreadyPresent(tmin, tmax, queryEVTPath, blocksize)


        # Test 4 - partial missing data
        #      =================
        # ^               ^
        tmin = 57032 # 2015-01-10T00:00:00
        tmax = 57096 # 2015-03-15T00:00:00
        assert DataStatus.MISSING == agdataset.dataIsAlreadyPresent(tmin, tmax, queryEVTPath, blocksize)        

        # Test 5 - partial missing data on multiple lines
        #       =================
        # ^                
        #       =================
        #                       ^                
        tmin = 58984 # 2020-05-15T00:00:00
        tmax = 59030 # 2020-06-30T00:00:00
        assert DataStatus.MISSING == agdataset.dataIsAlreadyPresent(tmin, tmax, queryEVTPath, blocksize)   


        # Test 5 - totally missing data
        #       =================
        # ^  ^               
        tmin = 57032 # 2015-01-10T00:00:00
        tmax = 57042 # 2015-01-20T00:00:00
        assert DataStatus.MISSING == agdataset.dataIsAlreadyPresent(tmin, tmax, queryEVTPath, blocksize)        

    
        
    @pytest.mark.testdir("core")
    def test_extract_data_log(self, logger):
        
        queryLOGPath = Path( __file__ ).absolute().parent.joinpath("test_data", "test_extract_data_LOG.qfile")

        agdataset = AGDataset(logger)

        blocksize = 1

        # TODO: impklement me!11!11!!!!!


    @pytest.mark.testdir("core")
    def test_compute_ssdc_slots(self, logger):

        agdataset = AGDataset(logger)

        ################## EVT FILES

        tmin = 58285 # 2018-Jun-16 00:00:00
        tmax = 58386 # 2018-Sep-25 00:00:00
        slots = agdataset.computeEVT_SSDCslots(tmin, tmax)

        #TODO: fixme
        expectedSlots = ['2018-06-15 00:00:00 2018-06-30 00:00:00', '2018-06-30 00:00:00 2018-07-15 00:00:00', '2018-07-15 00:00:00 2018-07-31 00:00:00', '2018-07-31 00:00:00 2018-08-15 00:00:00', '2018-08-15 00:00:00 2018-08-31 00:00:00', '2018-08-31 00:00:00 2018-09-15 00:00:00', '2018-09-15 00:00:00 2018-09-30 00:00:00']
        for index, slot in slots.iterrows():
            assert f"{slot['tmin']} {slot['tmax']}" == expectedSlots[index]

        tmin = 58849 # 2020-Jan-01 00:00:00
        tmax = 58955 # 2020-Apr-16 00:00:00
        slots = agdataset.computeEVT_SSDCslots(tmin, tmax)              
        #TODO: fixme
        expectedSlots = ['2019-12-31 00:00:00 2020-01-15 00:00:00', '2020-01-15 00:00:00 2020-01-31 00:00:00', '2020-01-31 00:00:00 2020-02-15 00:00:00', '2020-02-15 00:00:00 2020-02-29 00:00:00', '2020-02-29 00:00:00 2020-03-15 00:00:00', '2020-03-15 00:00:00 2020-03-31 00:00:00', '2020-03-31 00:00:00 2020-04-15 00:00:00', '2020-04-15 00:00:00 2020-04-30 00:00:00']
        for index, slot in slots.iterrows():
            assert f"{slot['tmin']} {slot['tmax']}" == expectedSlots[index]


        ################## LOG FILES
        
        tmin = 58285 # 2018-Jun-16 00:00:00
        tmax = 58290 # 2018-jun-21 00:00:00
        slots = agdataset.computeLOG_SSDCslots(tmin, tmax)
        expectedSlots = ['2018-06-16 00:00:00 2018-06-17 00:00:00', '2018-06-17 00:00:00 2018-06-18 00:00:00', '2018-06-18 00:00:00 2018-06-19 00:00:00', '2018-06-19 00:00:00 2018-06-20 00:00:00', '2018-06-20 00:00:00 2018-06-21 00:00:00', '2018-06-21 00:00:00 2018-06-22 00:00:00']
        for index, slot in slots.iterrows():
            assert f"{slot['tmin']} {slot['tmax']}" == expectedSlots[index]
        
        tmin = 58239 # 2018-05-01 00:00:00
        tmax = 58243 # 2018-05-05 00:00:00
        slots = agdataset.computeLOG_SSDCslots(tmin, tmax)
        expectedSlots = ['2018-05-01 00:00:00 2018-05-02 00:00:00', '2018-05-02 00:00:00 2018-05-03 00:00:00', '2018-05-03 00:00:00 2018-05-04 00:00:00', '2018-05-04 00:00:00 2018-05-05 00:00:00', '2018-05-05 00:00:00 2018-05-06 00:00:00']
        for index, slot in slots.iterrows():
            assert f"{slot['tmin']} {slot['tmax']}" == expectedSlots[index]
        

    @pytest.mark.testdir("core")
    def test_update_qfiles_not_empty(self, logger): # with duplicates

        agdataset = AGDataset(logger)
        
        queryEVTPath = Path( __file__ ).absolute().parent.joinpath("test_data", "EVT.qfile")
        queryEVTPathOut = Path( __file__ ).absolute().parent.joinpath("test_out", "EVT.qfile.out")

        queryLOGPath = Path( __file__ ).absolute().parent.joinpath("test_data", "LOG.qfile")
        queryLOGPathOut = Path( __file__ ).absolute().parent.joinpath("test_out", "LOG.qfile.out")

        tmin = 58849 # 2020-Jan-01 00:00:00
        tmax = 58955 # 2020-Apr-16 00:00:00

        agdataset.updateQfile(queryEVTPath, tmin, tmax, queryEVTPathOut)
        agdataset.updateQfile(queryLOGPath, tmin, tmax, queryLOGPathOut)

        with open(queryEVTPathOut, "r") as qf:
           assert len(qf.readlines()) == 10

        with open(queryLOGPathOut, "r") as qf:
           assert len(qf.readlines()) == 109


    @pytest.mark.testdir("core")
    def test_update_qfiles_empty(self, logger):

        agdataset = AGDataset(logger)
        
        queryEVTPath = Path( __file__ ).absolute().parent.joinpath("test_data", "test_update_qfiles_empty_EVT.qfile")
        queryEVTPathOut = Path( __file__ ).absolute().parent.joinpath("test_out", "test_update_qfiles_empty_EVT.qfile.out")

        queryLOGPath = Path( __file__ ).absolute().parent.joinpath("test_data", "test_update_qfiles_empty_LOG.qfile")
        queryLOGPathOut = Path( __file__ ).absolute().parent.joinpath("test_out", "test_update_qfiles_empty_LOG.qfile.out")

        tmin = 58849 # 2020-Jan-01 00:00:00
        tmax = 58955 # 2020-Apr-16 00:00:00
        agdataset.updateQfile(queryEVTPath, tmin, tmax, queryEVTPathOut)

        agdataset.updateQfile(queryLOGPath, tmin, tmax, queryLOGPathOut)

        with open(queryEVTPathOut, "r") as qf:
           assert len(qf.readlines()) == 8


    @pytest.mark.testdir("core")
    def test_update_qfiles_overwrite(self, logger):

        agdataset = AGDataset(logger)
        
        queryEVTPath = Path( __file__ ).absolute().parent.joinpath("test_out", "overwrite_EVT.qfile")
        queryLOGPath = Path( __file__ ).absolute().parent.joinpath("test_out", "overwrite_LOG.qfile")
        with open(queryEVTPath, "w") as inf:
            inf.write("""2020-01-15T00:00:00 2020-01-31T00:00:00
2020-03-15T00:00:00 2020-03-31T00:00:00""")
        with open(queryLOGPath, "w") as infLOG:
            infLOG.write("""2020-01-15T00:00:00 2020-01-31T00:00:00
2020-03-15T00:00:00 2020-03-31T00:00:00""")

        

        queryEVTPathOut = Path( __file__ ).absolute().parent.joinpath("test_out", "overwrite_EVT.qfile")
        queryLOGPathOut = Path( __file__ ).absolute().parent.joinpath("test_out", "overwrite_LOG.qfile")

        tmin = 58849 # 2020-Jan-01 00:00:00
        tmax = 58955 # 2020-Apr-16 00:00:00
        agdataset.updateQfile(queryEVTPath, tmin, tmax, queryEVTPathOut)
        agdataset.updateQfile(queryLOGPath, tmin, tmax, queryLOGPathOut)

        with open(queryEVTPathOut, "r") as qf:
           assert len(qf.readlines()) == 10

        with open(queryLOGPathOut, "r") as qf:
           assert len(qf.readlines()) == 109