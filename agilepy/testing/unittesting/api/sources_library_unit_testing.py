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
from pathlib import Path
import os
import shutil

from agilepy.api import SourcesLibrary


class SourcesLibraryUnittesting(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")
        self.sourcesconfPath = os.path.join(self.currentDirPath,"conf/sourceconf.xml")

        outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/api"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

        self.sl = SourcesLibrary()

    def test_load_xml(self):
        self.assertEqual(True, self.sl.loadSourceLibraryXML(self.sourcesconfPath))

    def test_source_file_parsing(self):

        res = SourcesLibrary.parseSourceFile("./agilepy/testing/unittesting/api/data/testcase0.source")
        self.assertEqual(True, bool(res))

        res = SourcesLibrary.parseSourceFile("./agilepy/testing/unittesting/api/data/testcase_2AGLJ2021+4029.source")
        self.assertEqual(True, bool(res))


    def test_select_sources_with_selection_string(self):

        self.sl.loadSourceLibraryXML(self.sourcesconfPath)
        self.assertEqual(2, len(self.sl.sources))

        sources = self.sl.selectSources('Name == "2AGLJ2021+4029"')
        self.assertEqual(1, len(sources))

        source = SourcesLibrary.parseSourceFile("./agilepy/testing/unittesting/api/data/testcase_2AGLJ2021+4029.source")
        self.sl.updateMulti(source, 80, 0)

        sources = self.sl.selectSources('Name == "2AGLJ2021+4029" AND Dist > 0 AND Flux > 0')
        self.assertEqual(1, len(sources))




    def test_select_sources_with_selection_lambda(self):

        self.sl.loadSourceLibraryXML(self.sourcesconfPath)


        sources = self.sl.selectSources( lambda Name : Name == "2AGLJ2021+4029" )
        self.assertEqual(1, len(sources))

        source = SourcesLibrary.parseSourceFile("./agilepy/testing/unittesting/api/data/testcase_2AGLJ2021+4029.source")
        self.sl.updateMulti(source, 80, 0)

        sources = self.sl.selectSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0)
        self.assertEqual(1, len(sources))




    def test_free_sources_with_selection_string(self):

        self.sl.loadSourceLibraryXML(self.sourcesconfPath)
        source = SourcesLibrary.parseSourceFile("./agilepy/testing/unittesting/api/data/testcase_2AGLJ2021+4029.source")
        self.sl.updateMulti(source, 80, 0)


        sources = self.sl.freeSources('Name == "2AGLJ2021+4029" AND Dist > 0 AND Flux > 0', "Flux", False)
        self.assertEqual(False, sources[0].spectrum.getFreeAttributeValueOf("name", "Flux"))


        sources = self.sl.freeSources('Name == "2AGLJ2021+4029" AND Dist > 0 AND Flux > 0', "Flux", True)
        self.assertEqual(True, sources[0].spectrum.getFreeAttributeValueOf("name", "Flux"))

        sources = self.sl.freeSources('Name == "2AGLJ2021+4029" AND Dist > 0 AND Flux > 0', "Index", True)
        self.assertEqual(True, sources[0].spectrum.getFreeAttributeValueOf("name", "Index"))

        sources = self.sl.freeSources('Name == "2AGLJ2021+4029" AND Dist > 0 AND Flux > 0', "Index", False)
        self.assertEqual(False, sources[0].spectrum.getFreeAttributeValueOf("name", "Index"))



    def test_free_sources_with_selection_lambda(self):

        self.sl.loadSourceLibraryXML(self.sourcesconfPath)
        source = SourcesLibrary.parseSourceFile("./agilepy/testing/unittesting/api/data/testcase_2AGLJ2021+4029.source")
        self.sl.updateMulti(source, 80, 0)


        sources = self.sl.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0, "Flux", False)
        self.assertEqual(False, sources[0].spectrum.getFreeAttributeValueOf("name", "Flux"))

        sources = self.sl.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0, "Flux", True)
        self.assertEqual(True, sources[0].spectrum.getFreeAttributeValueOf("name", "Flux"))

        sources = self.sl.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0, "Index", True)
        self.assertEqual(True, sources[0].spectrum.getFreeAttributeValueOf("name", "Index"))

        sources = self.sl.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0, "Index", False)
        self.assertEqual(False, sources[0].spectrum.getFreeAttributeValueOf("name", "Index"))


if __name__ == '__main__':
    unittest.main()
