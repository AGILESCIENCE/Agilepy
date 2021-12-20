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
import unittest # WHATTT! TODO: REMOVE ME
from pathlib import Path

from agilepy.utils.AGRest import AGRest 

class TestAGRest:

    """
    def test_request_data(logger):
        tmin = 55513.0005
        tmax = 55521
        agrest = AGRest(logger)
        data = agrest.requestData(tmin, tmax)
        assert Path(data).is_file() == True
    """

    @pytest.mark.testdir("utils")
    def test_extract_data(self, logger, gettmpdir):

        inputTarFile = Path( __file__ ).absolute().parent.joinpath("data", "1640011226033.tar")

        agrest = AGRest(logger)

        agrest._extractData(inputTarFile, gettmpdir)

        evtData = gettmpdir.joinpath("EVT")
        logData = gettmpdir.joinpath("LOG")

        assert len(os.listdir(evtData)) > 3
        assert len(os.listdir(logData)) > 3        


    def test_generate_index(self, logger):

        agrest = AGRest(logger)
        
        outDir = Path( __file__ ).absolute().parent.joinpath("tmp")
        outDir.mkdir(exist_ok=True, parents=True)

        evt = outDir.joinpath("EVT.index")
        log = outDir.joinpath("LOG.index")

        assert evt.is_file() == True 
        assert log.is_file() == True

        assert 69 == sum(1 for line in open(evt))
        assert 666 == sum(1 for line in open(log))  
