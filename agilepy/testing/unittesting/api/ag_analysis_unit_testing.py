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
import os
import shutil
from pathlib import Path

from agilepy.api.AGAnalysis import AGAnalysis

class AGAnalysisUnittesting(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")
        self.sourcesconfPath = os.path.join(self.currentDirPath,"conf/sourceconf.xml")

        outDir = Path(os.path.join(os.environ["AGILE"], "agilepy-test-data/unittesting-output/api"))

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

        self.aga = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)


    def test_analysis_pipeline(self):
        maplistFilePath = self.aga.generateMaps()
        self.assertEqual(True, os.path.isfile(maplistFilePath))

        products_1 = self.aga.mle(maplistFilePath)
        for p in products_1:
            self.assertEqual(True, os.path.isfile(p))

        products_2 = self.aga.mle(maplistFilePath)
        for p in products_2:
            self.assertEqual(True, os.path.isfile(p))

    def test_source_dist_updated_after_mle(self):
        maplistFilePath = self.aga.generateMaps()

        self.aga.mle(maplistFilePath)
        source_1 = self.aga.selectSources(lambda name: name == '2AGLJ2021+4029').pop()
        dist_1 = source_1.multi.get("multiDist")

        self.aga.setOptions(glon=81, glat=1)

        self.aga.mle(maplistFilePath)
        source_2 = self.aga.selectSources(lambda name: name == '2AGLJ2021+4029').pop()
        dist_2 = source_2.multi.get("multiDist")

        self.assertNotEqual(dist_1, dist_2)

    def test_source_Flux_updated_after_mle(self):

        maplistFilePath = self.aga.generateMaps()

        source_1 = self.aga.selectSources(lambda name: name == '2AGLJ2021+3654').pop()
        flux_1 = source_1.spectrum.get("flux")

        self.aga.mle(maplistFilePath)
        source_2 = self.aga.selectSources(lambda name: name == '2AGLJ2021+3654').pop()
        flux_2 = source_2.multi.get("multiFlux")

        self.assertNotEqual(flux_1, flux_2)

    def test_parse_maplistfile(self):
        self.aga.setOptions(energybins=[[100,300],[300,1000]], fovbinnumber=2)
        maplistFilePath = self.aga.generateMaps()

        maps_1 = self.aga.getSkyMaps()
        maps_2 = self.aga.getSkyMaps(maplistFilePath)

        self.assertEqual(4, len(maps_1))
        self.assertEqual(4, len(maps_2))

        for i in range(4):
            for j in range(3):
                self.assertEqual(maps_1[i][j], maps_2[i][j])

        for i in range(4):
            for j in range(3):
                self.assertEqual(True, os.path.isfile(maps_1[i][j]))

    def test_print_source(self):

        for s in self.aga.sourcesLibrary.sources:
            print(s)

        maplistFilePath = self.aga.generateMaps()

        self.aga.freeSources('name == "2AGLJ2021+3654"', "pos", True)

        self.aga.mle(maplistFilePath)

        for s in self.aga.sourcesLibrary.sources:
            print(s)

        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
