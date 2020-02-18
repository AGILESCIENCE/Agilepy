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
from typing import List
from pathlib import Path
from xml.etree.ElementTree import parse

from agilepy.api.SourcesLibrary import SourcesLibrary
from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.utils.CustomExceptions import SourceParamNotFoundError, SpectrumTypeNotFoundError,  \
                                           SourceModelFormatNotSupported

class SourcesLibraryUnittesting(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")
        self.xmlsourcesconfPath = os.path.join(self.currentDirPath,"conf/sourceconf.xml")
        self.agsourcesconfPath = os.path.join(self.currentDirPath,"conf/sourceconf.txt")

        self.config = AgilepyConfig()
        self.config.loadConfigurations(self.agilepyconfPath, validate=True)

        outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/api"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

        self.sl = SourcesLibrary()

    @staticmethod
    def get_free_params(source):

        return {
                 "curvature": source.spectrum.curvature.free,
                 "pivot_energy": source.spectrum.pivotEnergy.free,
                 "index": source.spectrum.index.free,
                 "pos": source.spatialModel.pos.free,
                 "flux": source.spectrum.flux.free
               }




    def test_get_supported_catalogs(self):
        files = self.sl.getSupportedCatalogs()
        self.assertEqual(1, len(files))
        catalog = files.pop()
        self.assertEqual("2AGL.multi", catalog)
        added = self.sl.loadSources(catalog)
        self.assertEqual(175, len(added))
        self.assertEqual(175, len(self.sl.sources))

    def test_load_file_with_wrong_extension(self):

        xmlsourcesconfPath = os.path.join(self.currentDirPath,"conf/sourceconf.wrongext")

        self.assertRaises(SourceModelFormatNotSupported, self.sl.loadSources, xmlsourcesconfPath)


    def test_load_wrong_file(self):

        xmlsourcesconfPath = os.path.join(self.currentDirPath,"conf/idontexitst.txt")

        self.assertRaises(FileNotFoundError, self.sl.loadSources, xmlsourcesconfPath)


    def test_load_catalog(self):

        catalogFile = "$AGILE/catalogs/2AGL.multi"

        added = self.sl.loadSources(catalogFile)

        self.assertEqual(175, len(added))
        self.assertEqual(175, len(self.sl.sources))


    def test_load_catalog_filtering_on_distances(self):

        catalogFile = "$AGILE/catalogs/2AGL.multi"

        added = self.sl.loadSources(catalogFile, rangeDist=(70, 80))

        self.assertEqual(15, len(added))
        self.assertEqual(15, len(self.sl.sources))


    def test_load_xml(self):

        added = self.sl.loadSources(self.xmlsourcesconfPath)

        self.assertEqual(2, len(added))
        self.assertEqual(2, len(self.sl.sources))

        sources = self.sl.selectSources('name == "2AGLJ2021+4029"')
        self.assertEqual(1, len(sources))
        source = sources.pop()
        self.assertEqual(119.3e-08, source.spectrum.get("flux"))
        self.assertEqual(1.75, source.spectrum.get("index"))
        self.assertEqual(78.2375, source.spatialModel.get("pos")[0])
        self.assertEqual(True, source.spatialModel.get("dist") > 0)


        sources = self.sl.selectSources('name == "2AGLJ2021+3654"')
        self.assertEqual(1, len(sources))
        source = sources.pop()
        self.assertEqual(70.89e-08, source.spectrum.get("flux"))
        self.assertEqual(1.38, source.spectrum.get("index"))
        self.assertEqual(75.2562, source.spatialModel.get("pos")[0])
        self.assertEqual(True, source.spatialModel.get("dist") > 0)

    def test_load_txt(self):
        agsourcesconfPath = os.path.join(self.currentDirPath,"conf/sourceconf_for_load_test.txt")

        added = self.sl.loadSources(agsourcesconfPath)

        self.assertEqual(10, len(added))
        self.assertEqual(10, len(self.sl.sources))

        sources = self.sl.selectSources('name == "2AGLJ1801-2334"')
        self.assertEqual(1, len(sources))
        source = sources.pop()

        self.assertEqual(3.579e-07, source.spectrum.get("flux"))
        self.assertEqual(3.37991, source.spectrum.get("index"))
        self.assertEqual(6.16978, source.spatialModel.get("pos")[0])



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

            self.assertDictEqual(fs[i], SourcesLibraryUnittesting.get_free_params(self.sl.sources[i]))

    def test_source_file_parsing(self):

        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+4029.source")

        res = self.sl.parseSourceFile(sourceFile)

        self.assertEqual(True, bool(res))

        self.assertEqual(True, isinstance(res.multiFlux.value, float))
        self.assertEqual(0, res.multiFlux.value)
        self.assertEqual(True, isinstance(res.multiSqrtTS.value, float))
        self.assertEqual(0, res.multiSqrtTS.value)
        self.assertEqual(None, res.multiDist.value)

        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")

        res = self.sl.parseSourceFile(sourceFile)
        self.assertEqual(True, bool(res))
        self.assertEqual(True, isinstance(res.multiFlux.value, float))
        self.assertEqual(6.69108e-15, res.multiFlux.value)
        self.assertEqual(None, res.multiDist.value)

    def test_select_sources_with_selection_string(self):

        self.sl.loadSources(self.xmlsourcesconfPath)
        self.assertEqual(2, len(self.sl.sources))

        sources = self.sl.selectSources('name == "2AGLJ2021+3654" AND dist > 0 AND flux > 0')
        self.assertEqual(1, len(sources))

        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")

        source = self.sl.parseSourceFile(sourceFile)

        self.sl.updateMulti(source)

        sources = self.sl.selectSources('name == "2AGLJ2021+3654" AND dist > 0 AND flux > 0')
        self.assertEqual(1, len(sources))

        """
        MAP sqrtTS con multiSqrtTS
        """
        sources = self.sl.selectSources('sqrtTS == 10')
        self.assertEqual(1, len(sources))

    def test_select_sources_with_selection_lambda(self):

        self.sl.loadSources(self.xmlsourcesconfPath)


        sources = self.sl.selectSources( lambda name : name == "2AGLJ2021+3654" )
        self.assertEqual(1, len(sources))

        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")

        source = self.sl.parseSourceFile(sourceFile)
        self.sl.updateMulti(source)

        sources = self.sl.selectSources(lambda name, dist, flux : name == "2AGLJ2021+3654" and dist > 0 and flux > 0)
        self.assertEqual(1, len(sources))

    def test_free_sources_with_selection_string(self):

        self.sl.loadSources(self.xmlsourcesconfPath)
        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")
        source = self.sl.parseSourceFile(sourceFile)
        self.sl.updateMulti(source)

        sources = self.sl.freeSources('name == "2AGLJ2021+3654" AND dist > 0 AND flux > 0', "flux", False)

        self.assertEqual(1, len(sources))
        self.assertEqual(0, sources[0].spectrum.getFree("flux"))
        self.assertEqual("0", sources[0].spectrum.getFree("flux", strRepr=True))


        sources = self.sl.freeSources('name == "2AGLJ2021+3654" AND dist > 0 AND flux > 0', "flux", True)
        self.assertEqual(1, sources[0].spectrum.getFree("flux"))
        self.assertEqual("1", sources[0].spectrum.getFree("flux", strRepr=True))


        sources = self.sl.freeSources('name == "2AGLJ2021+3654" AND dist > 0 AND flux > 0', "index", True)
        self.assertEqual(1, sources[0].spectrum.getFree("index"))
        self.assertEqual("1", sources[0].spectrum.getFree("index", strRepr=True))


        sources = self.sl.freeSources('name == "2AGLJ2021+3654" AND dist > 0 AND flux > 0', "index", False)
        self.assertEqual(0, sources[0].spectrum.getFree("index"))
        self.assertEqual("0", sources[0].spectrum.getFree("index", strRepr=True))


    def test_free_sources_with_selection_lambda(self):

        self.sl.loadSources(self.xmlsourcesconfPath)
        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")
        source = self.sl.parseSourceFile(sourceFile)
        self.sl.updateMulti(source)

        sources = self.sl.freeSources(lambda name, dist, flux : name == "2AGLJ2021+3654" and dist > 0 and flux > 0, "flux", False)
        self.assertEqual(1, len(sources))
        self.assertEqual(0, sources[0].spectrum.getFree("flux"))

        sources = self.sl.freeSources(lambda name, dist, flux : name == "2AGLJ2021+3654" and dist > 0 and flux > 0, "flux", True)
        self.assertEqual(1, sources[0].spectrum.getFree("flux"))

        sources = self.sl.freeSources(lambda name, dist, flux : name == "2AGLJ2021+3654" and dist > 0 and flux > 0, "index", True)
        self.assertEqual(1, sources[0].spectrum.getFree("index"))

        sources = self.sl.freeSources(lambda name, dist, flux : name == "2AGLJ2021+3654" and dist > 0 and flux > 0, "index", False)
        self.assertEqual(0, sources[0].spectrum.getFree("index"))

    def test_write_to_file_xml(self):

        self.config = AgilepyConfig()

        self.config.loadConfigurations(self.agilepyconfPath, validate=True)

        self.sl.loadSources(self.xmlsourcesconfPath)

        outfileName = "write_to_file_testcase"

        outputFile = Path(self.sl.writeToFile(outfileName, fileformat="xml"))

        self.assertEqual(True, outputFile.exists())

        sourcesxml = parse(outputFile).getroot()

        self.assertEqual(2, len(sourcesxml))

    def test_add_source(self):

        self.config = AgilepyConfig()

        self.config.loadConfigurations(self.agilepyconfPath, validate=True)

        self.sl.loadSources(self.xmlsourcesconfPath)

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


        self.assertEqual(True, self.sl.addSource("newsource", newSourceDict))

        newSource = self.sl.selectSources('name == "newsource"').pop()

        self.assertEqual(0, newSource.spectrum.get("flux"))
        self.assertEqual(0, newSource.spectrum.get("curvature"))
        self.assertEqual("newsource", newSource.name)

        newSourceDict = {
            "glon" : 250,
            "glat": 30,
            "spectrumType" : "LogParabola",
            "flux": 1,
            "curvature":2
        }
        self.assertEqual(True, self.sl.addSource("newsource2", newSourceDict))

        newSource = self.sl.selectSources('name == "newsource2"').pop()
        self.assertEqual(1, newSource.spectrum.get("flux"))
        self.assertEqual(2, newSource.spectrum.get("curvature"))
        self.assertEqual(250, newSource.spatialModel.get("pos")[0])
        self.assertEqual(30, newSource.spatialModel.get("pos")[1])
        self.assertEqual("newsource2", newSource.name)


        self.assertEqual(False, self.sl.addSource("newsource2", newSourceDict))


    def test_convert_catalog_to_xml(self):

        catalogFile = "$AGILE/catalogs/2AGL.multi"

        outfile = self.sl.convertCatalogToXml(catalogFile)

        sourcesxml = parse(outfile).getroot()

        self.assertEqual(175, len(sourcesxml))

        added = self.sl.loadSources(outfile)

        self.assertEqual(175, len(added))

        self.assertEqual(175, len(self.sl.sources))

if __name__ == '__main__':
    unittest.main()
