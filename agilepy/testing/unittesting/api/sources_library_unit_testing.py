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
                 "curvature": source.spectrum.getFreeAttributeValueOf("name", "Curvature"),
                 "pivot_energy": source.spectrum.getFreeAttributeValueOf("name", "PivotEnergy"),
                 "index": source.spectrum.getFreeAttributeValueOf("name", "Index"),
                 "pos": source.spatialModel.free,
                 "flux": source.spectrum.getFreeAttributeValueOf("name", "Flux")
               }

    def test_load_xml(self):
        self.assertEqual(True, self.sl.loadSources(self.xmlsourcesconfPath, fileformat="XML"))

        self.assertEqual(2, len(self.sl.sources))

        sources = self.sl.selectSources('Name == "2AGLJ2021+4029"')
        self.assertEqual(1, len(sources))
        source = sources.pop()
        self.assertEqual(119.3e-08, source.getParamValue("Flux"))
        self.assertEqual(1.75, source.getParamValue("Index"))
        self.assertEqual(78.2375, source.getParamValue("GLON"))
        self.assertEqual(True, source.spatialModel.dist > 0)


        sources = self.sl.selectSources('Name == "2AGLJ2021+3654"')
        self.assertEqual(1, len(sources))
        source = sources.pop()
        self.assertEqual(70.89e-08, source.getParamValue("Flux"))
        self.assertEqual(1.38, source.getParamValue("Index"))
        self.assertEqual(75.2562, source.getParamValue("GLON"))
        self.assertEqual(True, source.spatialModel.dist > 0)


    def test_load_txt(self):
        agsourcesconfPath = os.path.join(self.currentDirPath,"conf/sourceconf_for_load_test.txt")
        self.assertEqual(True, self.sl.loadSources(agsourcesconfPath, fileformat="AG"))
        self.assertEqual(10, len(self.sl.sources))

        sources = self.sl.selectSources('Name == "2AGLJ1801-2334"')
        self.assertEqual(10, len(sources))
        source = sources.pop()
        self.assertEqual(3.579e-07, source.getParamValue("Flux"))
        self.assertEqual(3.37991, source.getParamValue("Index"))
        self.assertEqual(6.16978, source.getParamValue("GLON"))



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
        self.assertEqual(True, isinstance(res.Flux, float))
        self.assertEqual(0, res.Flux)
        self.assertEqual(True, isinstance(res.SkytypeHFilterIrf, str))
        self.assertEqual('SKY002.SFMG_H0025', res.SkytypeHFilterIrf)
        self.assertEqual(True, isinstance(res.GalCoeff, List))
        self.assertEqual(4, len(res.GalCoeff))
        self.assertEqual(True, isinstance(res.GalCoeff[0], float))
        self.assertEqual(None, res.Dist)

        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")

        res = self.sl.parseSourceFile(sourceFile)
        self.assertEqual(True, bool(res))
        self.assertEqual(True, isinstance(res.Flux, float))
        self.assertEqual(6.69108e-15, res.Flux)
        self.assertEqual(True, isinstance(res.SkytypeHFilterIrf, str))
        self.assertEqual('SKY002.SFMG_H0025', res.SkytypeHFilterIrf)
        self.assertEqual(True, isinstance(res.GalCoeff, List))
        self.assertEqual(4, len(res.GalCoeff))
        self.assertEqual(True, isinstance(res.GalCoeff[0], float))
        self.assertEqual(None, res.Dist)

    def test_select_sources_with_selection_string(self):

        self.sl.loadSources(self.xmlsourcesconfPath, fileformat="XML")
        self.assertEqual(2, len(self.sl.sources))

        sources = self.sl.selectSources('Name == "2AGLJ2021+3654" AND Dist > 0 AND Flux > 0')
        self.assertEqual(1, len(sources))

        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")

        source = self.sl.parseSourceFile(sourceFile)
        self.sl.updateMulti(source)

        sources = self.sl.selectSources('Name == "2AGLJ2021+3654" AND Dist > 0 AND Flux > 0')
        self.assertEqual(1, len(sources))

        sources = self.sl.selectSources('SqrtTS == 10')
        self.assertEqual(1, len(sources))

    def test_select_sources_with_selection_lambda(self):

        self.sl.loadSources(self.xmlsourcesconfPath, fileformat="XML")


        sources = self.sl.selectSources( lambda Name : Name == "2AGLJ2021+3654" )
        self.assertEqual(1, len(sources))

        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")

        source = self.sl.parseSourceFile(sourceFile)
        self.sl.updateMulti(source)

        sources = self.sl.selectSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+3654" and Dist > 0 and Flux > 0)
        self.assertEqual(1, len(sources))

    def test_free_sources_with_selection_string(self):

        self.sl.loadSources(self.xmlsourcesconfPath, fileformat="XML")
        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")
        source = self.sl.parseSourceFile(sourceFile)
        self.sl.updateMulti(source)


        sources = self.sl.freeSources('Name == "2AGLJ2021+3654" AND Dist > 0 AND Flux > 0', "Flux", False)
        self.assertEqual(1, len(sources))
        self.assertEqual(0, sources[0].spectrum.getFreeAttributeValueOf("name", "Flux"))


        sources = self.sl.freeSources('Name == "2AGLJ2021+3654" AND Dist > 0 AND Flux > 0', "Flux", True)
        self.assertEqual(1, sources[0].spectrum.getFreeAttributeValueOf("name", "Flux"))

        sources = self.sl.freeSources('Name == "2AGLJ2021+3654" AND Dist > 0 AND Flux > 0', "Index", True)
        self.assertEqual(1, sources[0].spectrum.getFreeAttributeValueOf("name", "Index"))

        sources = self.sl.freeSources('Name == "2AGLJ2021+3654" AND Dist > 0 AND Flux > 0', "Index", False)
        self.assertEqual(0, sources[0].spectrum.getFreeAttributeValueOf("name", "Index"))

    def test_free_sources_with_selection_lambda(self):

        self.sl.loadSources(self.xmlsourcesconfPath, fileformat="XML")
        sourceFile = os.path.join(self.currentDirPath,"data/testcase_2AGLJ2021+3654.source")
        source = self.sl.parseSourceFile(sourceFile)
        self.sl.updateMulti(source)

        sources = self.sl.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+3654" and Dist > 0 and Flux > 0, "Flux", False)
        self.assertEqual(1, len(sources))
        self.assertEqual(0, sources[0].spectrum.getFreeAttributeValueOf("name", "Flux"))

        sources = self.sl.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+3654" and Dist > 0 and Flux > 0, "Flux", True)
        self.assertEqual(1, sources[0].spectrum.getFreeAttributeValueOf("name", "Flux"))

        sources = self.sl.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+3654" and Dist > 0 and Flux > 0, "Index", True)
        self.assertEqual(1, sources[0].spectrum.getFreeAttributeValueOf("name", "Index"))

        sources = self.sl.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+3654" and Dist > 0 and Flux > 0, "Index", False)
        self.assertEqual(0, sources[0].spectrum.getFreeAttributeValueOf("name", "Index"))

    def test_write_to_file_xml(self):

        self.config = AgilepyConfig()

        self.config.loadConfigurations(self.agilepyconfPath, validate=True)

        self.sl.loadSources(self.xmlsourcesconfPath, fileformat="XML")

        outDir = Path(self.config.getConf("output","outdir"))

        outDir.mkdir(parents=True, exist_ok=True)

        outputFile = Path(self.sl.writeToFile(outDir.joinpath("write_to_file_testcase"), fileformat="XML"))

        self.assertEqual(True, outputFile.exists())

        sourcesxml = parse(outputFile).getroot()

        self.assertEqual(2, len(sourcesxml))

if __name__ == '__main__':
    unittest.main()
