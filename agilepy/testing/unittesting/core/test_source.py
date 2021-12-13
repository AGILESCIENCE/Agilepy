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
from xml.etree.ElementTree import parse
from agilepy.core.source.Source import Source, PointSource
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.core.SourcesLibrary import SourcesLibrary


class SourceModelUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()

        self.test_logs_dir = Path(self.currentDirPath).joinpath("test_logs", "SourceModelUT")
        self.test_logs_dir.mkdir(parents=True, exist_ok=True)

        os.environ["TEST_LOGS_DIR"] = str(self.test_logs_dir)

        outDir = Path(os.path.join(os.environ["AGILE"])).joinpath("agilepy-test-data/unittesting-output/core")
        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

        self.sourcesTxt = os.path.join(self.currentDirPath,"test_data/sources.txt")
        self.sourcesXml = os.path.join(self.currentDirPath,"test_data/sources.xml")

        self.agilepyConf = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyConf)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.logger = AgilepyLogger()
        self.logger.initialize(self.config.getConf("output","outdir"), self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))

        self.sl = SourcesLibrary(self.config, self.logger)

    def test_parse_source_XML_format(self):

        xmlRoot = parse(self.sourcesXml).getroot()

        sources = []

        for sourceRoot in xmlRoot:

            source = Source.parseSourceXMLFormat(sourceRoot)
            
            sources.append(source)

        assert sources[0].get("flux")["value"] == 7.45398e-08
        assert sources[0].get("pos")["value"] == (92.4102, -10.3946)

        assert sources[1].get("flux")["value"] == 41.6072e-08
        assert sources[1].get("pos")["value"] == (119.677, 10.544)

        assert sources[2].get("flux")["value"] == 969.539e-08
        assert sources[2].get("index2")["value"] == 1.3477
        assert sources[2].get("index2")["free"] == 1
        assert sources[2].get("pos")["value"] == (263.585, -2.84083)

        assert sources[3].get("flux")["value"] == 35.79e-08
        assert sources[3].get("curvature")["value"] == 0.682363
        assert sources[3].get("curvature")["max"] == 3
        assert sources[3].get("pos")["value"] == (6.16978, -0.0676943)


    def test_parse_source_TXT_format(self):

        sources = []

        with open(self.sourcesTxt, "r") as txtFile:

            for line in txtFile:

                if line == "\n":
                    continue

                source = Source.parseSourceTXTFormat(line)

                sources.append(source)

        assert sources[0].name == "2AGLJ2021+4029"
        assert sources[0].get("flux")["value"] == 119.3e-08
        assert sources[0].get("pos")["value"] == (78.2375, 2.12298)

        assert sources[1].name == "2AGLJ2021+3654"
        assert sources[1].get("flux")["value"] == 70.89e-08
        assert sources[1].get("pos")["value"] == (75.2562, 0.151831)
