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


import unittest


from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.core.SourcesLibrary import SourcesLibrary
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.core.SourceModel import Source


class SourceModelUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()

        self.test_logs_dir = Path(self.currentDirPath).joinpath("test_logs", "SourceModelUT")
        self.test_logs_dir.mkdir(parents=True, exist_ok=True)

        os.environ["TEST_LOGS_DIR"] = str(self.test_logs_dir)

        outDir = Path(os.path.join(os.environ["AGILE"])).joinpath("agilepy-test-data/unittesting-output/core")
        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

        self.sourcesConfTxt = os.path.join(self.currentDirPath,"test_data/sourcesconf.txt")

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyConf)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.logger = AgilepyLogger()
        self.logger.initialize(self.config.getConf("output","outdir"), self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))

        self.sl = SourcesLibrary(self.config, self.logger)


    def test_get(self):

        added = self.sl.loadSourcesFromFile(self.sourcesConfTxt)

        for a in added:
            print(a)

        



