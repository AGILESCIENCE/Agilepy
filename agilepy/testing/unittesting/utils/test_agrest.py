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
from time import sleep
from agilepy.utils.AGRest import AGRest 
from agilepy.core.CustomExceptions import SSDCRestErrorDownload

class TestAGRest():

    """
    def test_request_data(logger):
        tmin = 55513.0005
        tmax = 55521
        agrest = AGRest(logger)
        data = agrest.requestData(tmin, tmax)
        assert Path(data).is_file() == True
    """
    @pytest.mark.ssdc
    @pytest.mark.testdir("utils", "test_gridfiles","ssdc")
    @pytest.mark.testlogsdir("utils/test_logs/test_gridfiles")
    def test_gridfiles(self, logger, gettmpdir):

        """
        To run this test --runrest it needed when calling pytest
        """

        agrest = AGRest(logger)

        tmin = 58051 # 2017-10-25 00:00:00.000
        tmax = 58055 # 2017-10-29 00:00:00.000

        sleep(3) # this sleep is to avoid too many requests ban
        outfile = agrest.gridFiles(tmin, tmax)

        filepath = Path(outfile)

        assert True == filepath.exists()

        filepath.unlink()

        assert False == filepath.exists()



    @pytest.mark.ssdc
    @pytest.mark.testdir("utils", "test_gridList")
    @pytest.mark.testlogsdir("utils/test_logs/test_gridlist")
    def test_gridList(self, logger, gettmpdir):


        """
        To run this test --runrest it needed when calling pytest
        """

        agrest = AGRest(logger)

        # Test data is available
        sleep(3) # this sleep is to avoid too many requests ban
        tmin = 58051 # 2017-10-25 00:00:00.000
        tmax = 58072 # 2017-11-15 00:00:00.000
        
        gridlist = agrest.gridList(tmin, tmax)
        assert len(gridlist) == 24

        # Test partially missing data
        sleep(3) # this sleep is to avoid too many requests ban
        tmax = 59030 # 2020-06-30 00:00:00.000

        with pytest.raises(SSDCRestErrorDownload):
            gridlist = agrest.gridList(tmin, tmax)
        
        # Test Missing Data
        sleep(3) # this sleep is to avoid too many requests ban

        tmin = 59062 # 2020-08-10T00:00:00.000
        tmax = 59077 # 2020-08-16 00:00:00.000

        with pytest.raises(SSDCRestErrorDownload):
            gridlist = agrest.gridList(tmin, tmax)
        

    @pytest.mark.ssdc
    @pytest.mark.testdir("utils", "test_datacoverage")
    @pytest.mark.testlogsdir("utils/test_logs/test_datacoverage")
    def test_datacoverage(self, logger, gettmpdir):

        """
        To run this test --runrest it needed when calling pytest
        """
        sleep(3) # this sleep is to avoid too many requests ban
        agrest = AGRest(logger)

        tmin, tmax = agrest.get_coverage()

        assert tmin == "2007-12-01T12:00:00"
        assert tmax == "2024-01-15T12:00:00"
