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

from agilepy.config import AgilepyConfig
from agilepy.api import AGAnalysis

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




    """
    aga.setOptions(binsize=99999)
    aga.printOptions("maps")
    aga.resetConf()
    # sources = aga.freeSources("Name == '2AGLJ0835-4514' and Dist > 0 and Flux > 0", "Flux", False)

    sources = aga.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0, "Flux", False)
    print("\n\nSource with Flux NOT freed: " )
    for s in sources:
        print(s)

    sources = aga.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0, "Flux", True)
    print("\n\nSource with Flux freed: " )
    for s in sources:
        print(s)


    print("\n\nNumber of sources: ", len(sourcesLib.getSources()))


    deleted = aga.deleteSources(lambda Name, Dist, Flux : Name == "2AGLJ2021+4029" and Dist > 0 and Flux > 0)
    print("\n\nDeleted sources:")
    for s in deleted:
        print(s)


    print("\n\nNumber of sources: ", len(sourcesLib.getSources()))
    """

if __name__ == '__main__':
    unittest.main()
