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

from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.core.SourcesLibrary import SourcesLibrary
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.core.source.Source import Source, PointSource

from agilepy.core.CustomExceptions import SourceParamNotFoundError, \
                                          SpectrumTypeNotFoundError,  \
                                          SourceModelFormatNotSupported, \
                                          MultiOutputNotFoundError

class SourcesLibraryUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()

        self.test_logs_dir = Path(self.currentDirPath).joinpath("test_logs", "SourcesLibraryUT")
        self.test_logs_dir.mkdir(parents=True, exist_ok=True)
        os.environ["TEST_LOGS_DIR"] = str(self.test_logs_dir)

        self.agilepyConf = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyConf)
        self.config.loadConfigurationsForClass("AGAnalysis")

        self.logger = AgilepyLogger()
        self.logger.initialize(self.config.getConf("output","outdir"), self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))

        outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/core"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

        self.sl = SourcesLibrary(self.config, self.logger)

    @staticmethod
    def get_free_params(source):

        return {
                 "curvature": source.spectrum.curvature["free"],
                 "pivot_energy": source.spectrum.pivotEnergy["free"],
                 "index": source.spectrum.index["free"],
                 "pos": source.spatialModel.pos["free"],
                 "flux": source.spectrum.flux["free"]
               }


    def test_load_file_with_wrong_extension(self):

        xmlsourcesconfPath = os.path.join(self.currentDirPath,"test_data/sourceconf.wrongext")

        self.assertRaises(SourceModelFormatNotSupported, self.sl.loadSourcesFromFile, xmlsourcesconfPath)

    def test_load_wrong_file(self):

        xmlsourcesconfPath = os.path.join(self.currentDirPath,"conf/idontexitst.txt")

        self.assertRaises(FileNotFoundError, self.sl.loadSourcesFromFile, xmlsourcesconfPath)

    def test_load_from_catalog(self):

        added = self.sl.loadSourcesFromCatalog("2AGL")
        self.assertEqual(175, len(added))
        self.assertEqual(175, len(self.sl.sources))

        self.assertRaises(FileNotFoundError, self.sl.loadSourcesFromCatalog, "paperino")

    def test_load_catalog_from_catalog_filtering_on_distances(self):

        added = self.sl.loadSourcesFromCatalog("2AGL", rangeDist=(70, 80))

        self.assertEqual(13, len(added))
        self.assertEqual(13, len(self.sl.sources))

        self.sl.sources = []
        added = self.sl.loadSourcesFromCatalog("2AGL", rangeDist=(0, 10))
        self.assertEqual(1, len(added))
        self.assertEqual(1, len(self.sl.sources))

        self.sl.sources = []
        added = self.sl.loadSourcesFromCatalog("2AGL", rangeDist=(0, 50))
        self.assertEqual(30, len(added))
        self.assertEqual(30, len(self.sl.sources))

    def test_load_sources_from_xml_file(self):
        
        added = self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.xml"))

        self.assertEqual(2, len(added))
        self.assertEqual(2, len(self.sl.sources))

        sources = self.sl.selectSources('name == "2AGLJ2021+4029"')
        self.assertEqual(1, len(sources))
        source = sources.pop()
        self.assertEqual(119.3e-08, source.spectrum.getVal("flux"))
        self.assertEqual(1.75, source.spectrum.getVal("index"))
        self.assertEqual(78.2375, source.spatialModel.getVal("pos")[0])
        self.assertEqual(True, source.spatialModel.getVal("dist") > 0)

        sources = self.sl.selectSources('name == "2AGLJ2021+3654"')
        self.assertEqual(1, len(sources))
        source = sources.pop()
        self.assertEqual(70.89e-08, source.spectrum.getVal("flux"))
        self.assertEqual(1.38, source.spectrum.getVal("index"))
        self.assertEqual(75.2562, source.spatialModel.getVal("pos")[0])
        self.assertEqual(True, source.spatialModel.getVal("dist") > 0)

    def test_load_sources_from_txt_file(self):

        added = self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.txt"))

        self.assertEqual(10, len(added))
        self.assertEqual(10, len(self.sl.sources))

        sources = self.sl.selectSources('name == "2AGLJ1801-2334"')
        self.assertEqual(1, len(sources))
        source = sources.pop()

        self.assertEqual(3.579e-07, source.spectrum.getVal("flux"))
        self.assertEqual(3.37991, source.spectrum.getVal("index"))
        self.assertEqual(6.16978, source.spatialModel.getVal("pos")[0])

        # testing fixflags
        f0 = {"curvature":0, "pivot_energy":0, "index":0, "pos":0, "flux":0} # special case
        f1 = {"curvature":0, "pivot_energy":0, "index":0, "pos":0, "flux":1}
        f2 = {"curvature":0, "pivot_energy":0, "index":0, "pos":1, "flux":0}
        f3 = {"curvature":0, "pivot_energy":0, "index":0, "pos":1, "flux":1}
        f4 = {"curvature":0, "pivot_energy":0, "index":1, "pos":0, "flux":0}
        f5 = {"curvature":0, "pivot_energy":0, "index":1, "pos":0, "flux":1}

        f7 = {"curvature":0, "pivot_energy":0, "index":1, "pos":1, "flux":1}

        f28 = {"curvature":1, "pivot_energy":1, "index":1, "pos":0, "flux":0}
        f30 = {"curvature":1, "pivot_energy":1, "index":1, "pos":1, "flux":0}
        f32 = {"curvature":0, "pivot_energy":0, "index":0, "pos":2, "flux":0} # special case

        fs = [f0,f1,f2,f3,f4,f5,f7,f28,f30,f32]

        for i in range(len(fs)):
            ff = i
            if ff == 6: ff = 7
            elif ff == 7: ff = 28
            elif ff == 8: ff = 30
            elif ff == 9: ff = 32

            self.assertDictEqual(fs[i], SourcesLibraryUT.get_free_params(self.sl.sources[i]))

    def test_source_file_parsing(self):

        sourceFile = os.path.join(self.currentDirPath,"test_data/testcase_2AGLJ0835-4514.source")

        res = self.sl.parseSourceFile(sourceFile)

        self.assertEqual(True, bool(res))

        self.assertEqual(True, isinstance(res.multiFlux["value"], float))
        self.assertEqual(9.07364e-06, res.multiFlux["value"])
        self.assertEqual(True, isinstance(res.multiSqrtTS["value"], float))
        self.assertEqual(2.17268, res.multiSqrtTS["value"])
        self.assertEqual(None, res.multiDist["value"])

    def test_load_source_from_catalog_without_scaling(self):

        sources = self.sl.loadSourcesFromCatalog(catalogName="2AGL")

        self.assertEqual(175, len(sources))

        self.assertEqual(7.45398e-08, sources[0].spectrum.getVal("flux"))

    def test_load_source_from_catalog_with_scaling(self):

        self.config.setOptions(emin_sources=10, emax_sources=1000)

        sources = self.sl.loadSourcesFromCatalog(catalogName="2AGL")

        self.assertEqual(175, len(sources))

        self.assertEqual(6.940938928095228e-07, sources[0].spectrum.getVal("flux"))

    def test_select_sources_with_selection_string(self):

        self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.xml"))
        self.assertEqual(2, len(self.sl.sources))
        
        sources = self.sl.selectSources('name == "2AGLJ2021+3654" AND flux > 0')
        self.assertEqual(1, len(sources))

        sourceFile = os.path.join(self.currentDirPath,"test_data/testcase_2AGLJ2021+3654.source")

        mleAnalysisResults = self.sl.parseSourceFile(sourceFile)

        self.sl.updateSourceWithMLEResults(mleAnalysisResults)

        sources = self.sl.selectSources('name == "2AGLJ2021+3654" AND flux > 0')
        self.assertEqual(1, len(sources))

        sources = self.sl.selectSources('multisqrtts == 10')
        self.assertEqual(1, len(sources))

        sources = self.sl.selectSources('sqrtts == 10')
        self.assertEqual(1, len(sources))


    def test_select_sources_with_selection_lambda(self):

        self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.xml"))

        sources = self.sl.selectSources( lambda name : name == "2AGLJ2021+3654" )
        self.assertEqual(1, len(sources))

        sourceFile = os.path.join(self.currentDirPath,"test_data/testcase_2AGLJ2021+3654.source")

        mleAnalysisResults = self.sl.parseSourceFile(sourceFile)

        self.sl.updateSourceWithMLEResults(mleAnalysisResults)

        sources = self.sl.selectSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0)
        self.assertEqual(1, len(sources))

    def test_free_sources_with_selection_string(self):

        self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.xml"))
        sourceFile = os.path.join(self.currentDirPath,"test_data/testcase_2AGLJ2021+3654.source")
        mleAnalysisResults = self.sl.parseSourceFile(sourceFile)
        self.sl.updateSourceWithMLEResults(mleAnalysisResults)

        sources = self.sl.freeSources('name == "2AGLJ2021+3654" AND flux > 0', "flux", False)

        self.assertEqual(1, len(sources))
        self.assertEqual(True, "flux" not in sources[0].getFreeParams())

        sources = self.sl.freeSources('name == "2AGLJ2021+3654" AND flux > 0', "flux", True)
        self.assertEqual(True, "flux" in sources[0].getFreeParams())

        sources = self.sl.freeSources('name == "2AGLJ2021+3654" AND flux > 0', "index", True)
        self.assertEqual(True, "index" in sources[0].getFreeParams())

        sources = self.sl.freeSources('name == "2AGLJ2021+3654" AND flux > 0', "index", False)
        self.assertEqual(True, "index" not in sources[0].getFreeParams())

    def test_free_sources_with_selection_lambda(self):

        self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.xml"))
        sourceFile = os.path.join(self.currentDirPath,"test_data/testcase_2AGLJ2021+3654.source")
        mleAnalysisResults = self.sl.parseSourceFile(sourceFile)
        self.sl.updateSourceWithMLEResults(mleAnalysisResults)

        sources = self.sl.freeSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0, "flux", False)
        self.assertEqual(1, len(sources))
        self.assertEqual(True, "flux" not in sources[0].getFreeParams())

        sources = self.sl.freeSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0, "flux", True)
        self.assertEqual(True, "flux" in sources[0].getFreeParams())

        sources = self.sl.freeSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0, "index", True)
        self.assertEqual(True, "index" in sources[0].getFreeParams())

        sources = self.sl.freeSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0, "index", False)
        self.assertEqual(True, "index" not in sources[0].getFreeParams())

    def test_write_to_file_xml(self):

        self.config = AgilepyConfig()

        self.config.loadBaseConfigurations(self.agilepyConf)

        self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.xml"))

        outfileName = "write_to_file_testcase"

        outputFile = Path(self.sl.writeToFile(outfileName, fileformat="xml"))

        self.assertEqual(True, outputFile.exists())

        sourcesxml = parse(outputFile).getroot()

        self.assertEqual(2, len(sourcesxml))

    def test_write_to_file_txt(self):

        self.config = AgilepyConfig()

        self.config.loadBaseConfigurations(self.agilepyConf)

        sourcesFile = os.path.join(self.currentDirPath,"test_data/sourcesconf_for_write_to_file_txt.txt")

        self.sl.loadSourcesFromFile(sourcesFile)

        outfileName = "write_to_file_testcase"

        outputFile = Path(self.sl.writeToFile(outfileName, fileformat="txt"))

        self.assertEqual(True, outputFile.exists())

        with open(outputFile) as of:
            lines = of.readlines()

        self.assertEqual("1.57017e-07 80.3286 1.12047 2.16619 0 2 _2AGLJ2032+4135 0 0 0 0 0.5 5.0 20 10000 0 100", lines[0].strip())
        self.assertEqual("1.69737e-07 79.9247 0.661449 1.99734 0 2 CYGX3 0 0 0 0 0.5 5.0 20 10000 0 100", lines[1].strip())
        self.assertEqual("1.19303e-06 78.2375 2.12298 1.75823 3 2 _2AGLJ2021+4029 0 1 3307.63 0 0.5 5.0 20.0 10000.0  0 100", lines[2].strip())

    def test_add_source(self):

        self.config = AgilepyConfig()

        self.config.loadBaseConfigurations(self.agilepyConf)

        self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.xml"))

        newSourceDict = {
            "a" : 10
        }
        self.assertRaises(SourceParamNotFoundError, self.sl.addSource, "newsource", newSourceDict)


        newSourceDict = {
            "glon" : 250,
            "glat": 30,
            "spectrumType" : "LogPaperone"
        }
        self.assertRaises(SpectrumTypeNotFoundError, self.sl.addSource, "newsource", newSourceDict)

        newSourceDict = {
            "glon" : 250,
            "glat": 30,
            "spectrumType" : "LogParabola"
        }
        self.assertRaises(SourceParamNotFoundError, self.sl.addSource, "", newSourceDict)
        self.assertRaises(SourceParamNotFoundError, self.sl.addSource, None, newSourceDict)
        self.assertRaises(SourceParamNotFoundError, self.sl.addSource, "newsource", newSourceDict)

        newSourceDict = {
            "glon" : 250,
            "glat": 30,
            "spectrumType" : "LogParabola",
            "flux": 40,
            "index": 2,
            "pivotEnergy": 4,
            "curvature": 5
        }
        newSourceObj = self.sl.addSource("newsource", newSourceDict)

        self.assertEqual(True, isinstance(newSourceObj, PointSource))

        newSource = self.sl.selectSources('name == "newsource"').pop()

        self.assertEqual(40, newSource.spectrum.getVal("flux"))
        self.assertEqual(5, newSource.spectrum.getVal("curvature"))
        self.assertEqual("newsource", newSource.name)
        self.assertEqual(35.2462913047547, newSource.spatialModel.getVal("dist"))


    def test_convert_catalog_to_xml(self):

        catalogFile = "$AGILE/catalogs/2AGL.multi"

        outfile = self.sl.convertCatalogToXml(catalogFile)

        sourcesxml = parse(outfile).getroot()

        self.assertEqual(175, len(sourcesxml))

        added = self.sl.loadSourcesFromFile(outfile)

        self.assertEqual(175, len(added))

        self.assertEqual(175, len(self.sl.sources))

    def test_backup_restore(self):
        self.config = AgilepyConfig()

        self.config.loadBaseConfigurations(self.agilepyConf)

        self.sl.loadSourcesFromFile(os.path.join(self.currentDirPath,"test_data/sources_2.xml"))

        """
        for s in self.sl.getSources():
            print(s)
        """
        
        self.assertEqual(2, len(self.sl.sources))

        self.sl.backupSL()

        self.sl.deleteSources('name=="2AGLJ2021+4029"')

        self.assertEqual(1, len(self.sl.sources))

        self.sl.deleteSources('name=="2AGLJ2021+3654"')

        self.assertEqual(0, len(self.sl.sources))

        self.sl.restoreSL()

        self.assertEqual(2, len(self.sl.sources))


if __name__ == '__main__':
    unittest.main()