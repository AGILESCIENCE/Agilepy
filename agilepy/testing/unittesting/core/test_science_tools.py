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
from agilepy.config import AgilepyConfig
from agilepy.core.ScienceTools import Indexgen
from agilepy.core.ScienceTools import Spotfinder

class TestSourceModel:

    @pytest.mark.testdir("core", "test_indexgen")
    def test_indexgen(self, config, logger, testdataset):

        indexgen = Indexgen("AG_indexgen", logger)

        args = {
            "data_dir": testdataset["log"],
            "type": "log",
            "out_dir": str(Path( __file__ ).absolute().parent.joinpath("test_out")),
            "out_file": "INDEX.LOG"
        }


        indexgen.configureTool(config, args)


        products = indexgen.call()

        expected_output_file = str(Path(args["out_dir"]).joinpath(args["out_file"]))

        
        assert (expected_output_file in products) == True
        assert Path(expected_output_file).exists() == True

class TestSpotFinder:
    

    @pytest.mark.skip(reason="This test starts and gets stuck")
    @pytest.mark.testdir("core", "test_spotfinder")
    def test_spotfinder(self, config, logger):

        current_path = Path(__file__).parent.resolve()
        current_path = current_path.joinpath("test_data")
        print(config)

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(config)


        spotfinder = Spotfinder("AG_spotfinder", logger)
        
        args = {
            "input_file": f"{current_path}/testcase_EMIN00100_EMAX00300_01.cts.gz",
            "input_binsize": 0.5,
            "smoothing": 2,
            "max_region": 10,
            "output_files": "MLE0000hypothesis1.multi",
            "algorithm": 1,
            "remove_spot": 2,
            "sky_segmentation": 0,
            "shift_to_north": 0,
            "remove_sources": 50.0,
            "exp_filename": f"{current_path}/testcase_EMIN00100_EMAX00300_01.exp.gz",
            "min_exp": 50
        }
        
        spotfinder.configureTool(self.config, args)

        products = spotfinder.call()

        self.expectedmulti = str(Path(self.config.getOptionValue("outdir")).joinpath(args["output_files"]))
        self.expectedreg = str(Path(self.config.getOptionValue("outdir")).joinpath(args["output_files"]))+".reg"
        
        assert Path(self.expectedmulti).exists() == True
        assert Path(self.expectedreg).exists() == True
