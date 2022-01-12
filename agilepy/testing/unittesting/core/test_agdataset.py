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
from agilepy.core.AGDataset import AGDataset 
from agilepy.core.AGDataset import DataStatus

class TestAGDataset:

    @pytest.mark.testdir("core")
    def test_extract_data(self, logger):

        queryEVTPath = Path( __file__ ).absolute().parent.joinpath("test_data", "queryEVT.qfile")
        queryLOGPath = Path( __file__ ).absolute().parent.joinpath("test_data", "queryLOG.qfile")

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
    def test_compute_ssdc_slots(self, logger):

        agdataset = AGDataset(logger)

        tmin = 58285 # 2018-Jun-16 00:00:00
        tmax = 58386 # 2018-Sep-25 00:00:00
        slots = agdataset.computeSSDCslots(tmin, tmax)

        expectedSlots = ['2018-06-15 00:00:00  2018-06-30 00:00:00', '2018-06-30 00:00:00 2018-07-15 00:00:00', '2018-07-15 00:00:00  2018-07-31 00:00:00', '2018-07-31 00:00:00 2018-08-15 00:00:00', '2018-08-15 00:00:00  2018-08-31 00:00:00', '2018-08-31 00:00:00 2018-09-15 00:00:00', '2018-09-15 00:00:00  2018-09-30 00:00:00']
        for i, slot in enumerate(slots):  
            assert str(slot) == expectedSlots[i]


        tmin = 58849 # 2020-Jan-01 00:00:00
        tmax = 58955 # 2020-Apr-16 00:00:00
        slots = agdataset.computeSSDCslots(tmin, tmax)              
        expectedSlots = ['2019-12-31 00:00:00 2020-01-15 00:00:00', '2020-01-15 00:00:00  2020-01-31 00:00:00', '2020-01-31 00:00:00 2020-02-15 00:00:00', '2020-02-15 00:00:00  2020-02-29 00:00:00', '2020-02-29 00:00:00 2020-03-15 00:00:00', '2020-03-15 00:00:00  2020-03-31 00:00:00', '2020-03-31 00:00:00 2020-04-15 00:00:00', '2020-04-15 00:00:00  2020-04-30 00:00:00']
        for i, slot in enumerate(slots):  
            assert str(slot) == expectedSlots[i]        

        