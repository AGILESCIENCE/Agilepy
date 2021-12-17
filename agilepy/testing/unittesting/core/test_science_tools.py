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
from pathlib import Path 

from agilepy.core.ScienceTools import Indexgen

class TestSourceModel:

    @pytest.mark.testdir("core")
    def test_indexgen(self, config, logger, testdataset):

        indexgen = Indexgen("AG_indexgen", logger)

        args = {
            "log_dir": testdataset["log"],
            "type": "log",
            "out_dir": str(Path( __file__ ).absolute().parent),
            "out_file": "INDEX.LOG"
        }

        indexgen.configureTool(config, args)


        products = indexgen.call()

        expected_output_file = str(Path(args["out_dir"]).joinpath(args["out_file"]))

        assert products[expected_output_file] == 1
        assert (expected_output_file in products) == True
        assert Path(expected_output_file).exists() == True
