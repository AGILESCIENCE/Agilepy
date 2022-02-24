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
import pytest
import unittest
from pathlib import Path
from xml.etree.ElementTree import parse

from agilepy.core.source.Source import Source, PointSource
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.core.SourcesLibrary import SourcesLibrary
from agilepy.core.source.Spectrum import Spectrum
from agilepy.core.CustomExceptions import SourceParameterNotFound


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


    def test_init(self):

        source = PointSource(name="test-source")
        source.spectrum = Spectrum.getSpectrum("PowerLaw")
        assert "PointSource" == type(source.spatialModel).__name__

    def test_get(self):

        source = PointSource(name="test-source")
        source.spectrum = Spectrum.getSpectrum("PowerLaw")
        assert "PointSource" == type(source.spatialModel).__name__

        assert len(source.get("flux").keys()) == 6
        assert source.getVal("flux") == None

        with pytest.raises(SourceParameterNotFound):
            source.get("fluxxx")
            
        with pytest.raises(SourceParameterNotFound):
            source.getVal("fluxxx")


    def test_set(self):

        source = PointSource(name="test-source")
        source.spectrum = Spectrum.getSpectrum("PowerLaw")
        assert "PointSource" == type(source.spatialModel).__name__
        
        source.set("flux", {"min": 1}) 
        source.setVal("flux", 10) 
        assert source.spectrum.flux["min"] == 1
        assert source.spectrum.flux["value"] == 10

        with pytest.raises(SourceParameterNotFound):
            source.set("fluxxx", {"value": 10})

        with pytest.raises(ValueError):
            source.set("fluxxx", 10)

        with pytest.raises(SourceParameterNotFound):
            source.setVal("fluxxx", 100)


    def test_str(self):
        source = PointSource(name="test-source")
        source.spectrum = Spectrum.getSpectrum("PowerLaw")
        source.setVal("flux", 100) 
        source.setVal("index", 1000) 
        source.setVal("pos", (30,15)) 

        print(source)
        
        """
        sourceStrComponents = str(source).split("\n")
        assert sourceStrComponents[0] == ''
        assert sourceStrComponents[1] == "-----------------------------------------------------------"
        assert sourceStrComponents[2] == "Source name: test-source (PointSource)"
        assert sourceStrComponents[3] == "  * Spectrum type: PowerLaw"
        assert sourceStrComponents[4] == "  * Free parameters: none"
        assert sourceStrComponents[5] == "  * Initial source parameters:"
        assert sourceStrComponents[6] == "	- flux (ph/cm2s): 1.0000e+02"
        assert sourceStrComponents[7] == "	- index : 1000"
        assert sourceStrComponents[8] == "	- Source position (l,b): (30, 15)"
        """
