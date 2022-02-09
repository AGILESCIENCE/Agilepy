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
    def test_gridfiles(self, logger, gettmpdir):

        """
        To run this test --runrest it needed when calling pytest
        """

        agrest = AGRest(logger)

        tmin = 58051
        tmax = 58055

        outfile = agrest.gridFiles(tmin, tmax)

        filepath = Path(outfile)

        assert True == filepath.exists()

        filepath.unlink()

        assert False == filepath.exists()



    @pytest.mark.ssdc
    @pytest.mark.testdir("utils", "test_gridList")
    def test_gridList(self, logger, gettmpdir):


        """
        To run this test --runrest it needed when calling pytest
        """

        agrest = AGRest(logger)

        tmin = 58051
        tmax = 58072
        
        gridlist = agrest.gridList(tmin, tmax)

        assert len(gridlist) == 24

        tmax = 58200

        with pytest.raises(SSDCRestErrorDownload):
            gridlist = agrest.gridList(tmin, tmax)

        tmin = 59549
        tmax = 59569

        with pytest.raises(SSDCRestErrorDownload):
            gridlist = agrest.gridList(tmin, tmax)

    @pytest.mark.ssdc
    @pytest.mark.testdir("utils", "test_datacoverage")
    def test_datacoverage(self, logger, gettmpdir):

        """
        To run this test --runrest it needed when calling pytest
        """

        agrest = AGRest(logger)

        tmin, tmax = agrest.get_coverage()

        print(tmin, tmax)

        assert tmin == "2007-12-01T12:00:00"



        
        
