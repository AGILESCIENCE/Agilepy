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
import shutil
import unittest
from pathlib import Path
from agilepy.core.SourceModel import Source
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.core.SourceModel import MultiOutput
from agilepy.core.SourcesLibrary import SourcesLibrary
from agilepy.core.CustomExceptions import SourceAttributeNotFound, AttributeNotManuallyUpdatable


class SourceModelUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()

        self.test_logs_dir = Path(self.currentDirPath).joinpath("test_logs", "SourceModelUT")
        self.test_logs_dir.mkdir(parents=True, exist_ok=True)

        os.environ["TEST_LOGS_DIR"] = str(self.test_logs_dir)

        outDir = Path(os.path.join(os.environ["AGILE"])).joinpath("agilepy-test-data/unittesting-output/core")
        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

        self.sourcesConfTxt = os.path.join(self.currentDirPath,"test_data/sourceconf.txt")
        self.agilepyConf = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyConf)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.logger = AgilepyLogger()
        self.logger.initialize(self.config.getConf("output","outdir"), self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))

        self.sl = SourcesLibrary(self.config, self.logger)


    def test_get(self):

        source = self.sl.loadSourcesFromFile(self.sourcesConfTxt).pop()

        assert 960.59 == source.get("cutoffEnergy")

        print(source)
        assert (75.2562, 0.151831) == source.get("pos")
        assert  4.746224592316892 == source.get("dist")
        print(source.spatialModel.get("locationLimit"))
        assert 0 == source.get("locationLimit")

        # mle() has not been performed yet.
        self.assertRaises(SourceAttributeNotFound, source.get, "multiFluxNegErr")

        source.multi = MultiOutput()
        source.multi.multiFluxNegErr.setAttributes(value=666) 
        assert 666 == source.get("multiFluxNegErr")

        self.assertRaises(SourceAttributeNotFound, source.get, "DOGE")



    def test_set(self):

        source = self.sl.loadSourcesFromFile(self.sourcesConfTxt).pop()

        coenergy = 42
        assert True == source.set("cutoffEnergy", coenergy)
        assert  coenergy == source.get("cutoffEnergy")

        self.assertRaises(AttributeNotManuallyUpdatable, source.set, "pos", "(1, 1)")

        source.set("dist", 0.5)
        assert source.spatialModel.dist.value == 0.5

        source.set("locationLimit", 1)
        assert source.spatialModel.locationLimit.value == 1

        self.assertRaises(SourceAttributeNotFound, source.get, "multiFluxNegErr")

        source.multi = MultiOutput()
        source.set("multiFluxNegErr", 666)
        assert source.multi.multiFluxNegErr.value == 666