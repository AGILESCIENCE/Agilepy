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
from time import sleep

from agilepy.api.AGAnalysis import AGAnalysis

class AGAnalysisUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")
        self.sourcesconfPath = os.path.join(self.currentDirPath,"conf/sourceconf.xml")
        self.sourcesconfPathcalcBkg = os.path.join(self.currentDirPath,"conf/sourceconf_for_calcBkg.txt")
        outDir = Path(os.path.join(os.environ["AGILE"])).joinpath("agilepy-test-data/unittesting-output/api")

        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

    def test_generate_maps(self):

        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        outDir = ag.getOptionValue("outdir")

        maplistFilePath = ag.generateMaps()
        self.assertEqual(True, os.path.isfile(maplistFilePath))

        maps = os.listdir(outDir.joinpath("maps"))
        self.assertEqual(16, len(maps))

        lines = None
        with open(maplistFilePath) as mfp:
            lines = mfp.readlines()

        self.assertEqual(4, len(lines))

        ag.destroy()

    def test_update_gal_iso(self):

        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        outDir = ag.getOptionValue("outdir")

        ag.config.setOptions(galcoeff=[0.6, 0.8, 0.6, 0.8])
        ag.config.setOptions(isocoeff=[10, 15, 10, 15])

        galcoeffs = ag.config.getOptionValue("galcoeff")
        isocoeffs = ag.config.getOptionValue("isocoeff")

        maplistFilePath = ag.generateMaps()

        matrix = ag.parseMaplistFile()
        for idx, row in enumerate(matrix):
            self.assertEqual(str(galcoeffs[idx]), row[4])
            self.assertEqual(str(isocoeffs[idx]), row[5])

        if outDir.joinpath("maps").exists() and outDir.joinpath("maps").is_dir():
            shutil.rmtree(outDir.joinpath("maps"))

        outDir.joinpath("maps").mkdir(parents=False, exist_ok=True)

        ag.config.setOptions(galcoeff=[0,0,0,0])
        ag.config.setOptions(isocoeff=[0,0,0,0])

        galcoeffs = ag.config.getOptionValue("galcoeff")
        isocoeffs = ag.config.getOptionValue("isocoeff")

        matrix = ag.parseMaplistFile()
        for idx, row in enumerate(matrix):
            self.assertEqual(str(galcoeffs[idx]), row[4])
            self.assertEqual(str(isocoeffs[idx]), row[5])

        ag.destroy()

    def test_analysis_pipeline(self):
        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        maplistFilePath = ag.generateMaps()
        self.assertEqual(True, os.path.isfile(maplistFilePath))

        products_1 = ag.mle(maplistFilePath)
        for p in products_1:
            self.assertEqual(True, os.path.isfile(p))

        products_2 = ag.mle(maplistFilePath)
        for p in products_2:
            self.assertEqual(True, os.path.isfile(p))

        ag.destroy()

    def test_source_dist_updated_after_mle(self):
        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        maplistFilePath = ag.generateMaps()

        ag.mle(maplistFilePath)
        source_1 = ag.selectSources(lambda name: name == '2AGLJ2021+4029').pop()
        dist_1 = source_1.multi.get("multiDist")

        ag.setOptions(glon=81, glat=1)

        ag.mle(maplistFilePath)
        source_2 = ag.selectSources(lambda name: name == '2AGLJ2021+4029').pop()
        dist_2 = source_2.multi.get("multiDist")

        self.assertNotEqual(dist_1, dist_2)

        ag.destroy()

    def test_source_Flux_updated_after_mle(self):
        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        maplistFilePath = ag.generateMaps()

        source_1 = ag.selectSources(lambda name: name == '2AGLJ2021+3654').pop()
        flux_1 = source_1.spectrum.get("flux")

        ag.mle(maplistFilePath)
        source_2 = ag.selectSources(lambda name: name == '2AGLJ2021+3654').pop()
        flux_2 = source_2.multi.get("multiFlux")

        self.assertNotEqual(flux_1, flux_2)

        ag.destroy()

    def test_parse_maplistfile(self):
        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        ag.setOptions(energybins=[[100,300],[300,1000]], fovbinnumber=2)
        maplistFilePath = ag.generateMaps()

        maplistRows1 = ag.parseMaplistFile()
        maplistRows2 = ag.parseMaplistFile(maplistFilePath)

        self.assertEqual(4, len(maplistRows1))
        self.assertEqual(4, len(maplistRows2))

        for i in range(4):
            for j in range(3):
                self.assertEqual(maplistRows1[i][j], maplistRows2[i][j])

        for i in range(4):
            for j in range(3):
                self.assertEqual(True, os.path.isfile(maplistRows1[i][j]))

        ag.destroy()

    def test_print_source(self):
        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        maplistFilePath = ag.generateMaps()

        ag.freeSources('name == "2AGLJ2021+3654"', "pos", True)

        ag.mle(maplistFilePath)

        for s in ag.sourcesLibrary.sources:
            print(s)

        self.assertEqual(True, True)

        ag.destroy()

    def test_display_sky_maps(self):

        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)
        _ = ag.generateMaps()

        maps = ag.displayCtsSkyMaps(singleMode=False, saveImage=True)
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        maps = ag.displayExpSkyMaps(singleMode=False, saveImage=True)
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        maps = ag.displayGasSkyMaps(singleMode=False, saveImage=True)
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        ag.destroy()

    def test_display_sky_maps_singlemode(self):

        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)
        _ = ag.generateMaps()

        maps = ag.displayCtsSkyMaps(saveImage=True)
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        maps = ag.displayExpSkyMaps(saveImage=True)
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        maps = ag.displayGasSkyMaps(saveImage=True)
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        ag.destroy()

    def test_update_source_position(self):

        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        ag.generateMaps()


        ag.freeSources('name == "2AGLJ2021+4029"', "pos", False)

        ag.mle()


        self.assertRaises(ValueError, ag.updateSourcePosition, "2AGLJ2021+4029", useMulti=False)

        changed = ag.updateSourcePosition("2AGLJ2021+4029", useMulti=False, glon=78.2375, glat=2.12298)
        self.assertEqual(False, changed)


        ag.freeSources('name == "2AGLJ2021+4029"', "pos", True)

        ag.mle()

        changed = ag.updateSourcePosition("2AGLJ2021+4029", useMulti=True)
        self.assertEqual(False, changed)

        ag.destroy()


    """
    def test_lc(self):
        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)

        ag.setOptions(glon=78.2375, glat=2.12298)

        ag.setOptions(tmin=456361778.000000, tmax=456537945.000000, timetype="TT")

        ag.freeSources('name == "2AGLJ2021+4029"', "flux", True)

        lightCurveData = ag.lightCurve("2AGLJ2021+4029", binsize=90000)

        print(lightCurveData)

        self.assertEqual(True, os.path.isfile(lightCurveData))
    """

    """
    def test_display_sky_maps_singlemode_show(self):

        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPath)
        _ = ag.generateMaps()

        maps = ag.displayCtsSkyMaps(saveImage=False, catalogRegions="2AGL", catalogRegionsColor="red")
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        maps = ag.displayExpSkyMaps(saveImage=False, catalogRegions="2AGL", catalogRegionsColor="red")
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        maps = ag.displayGasSkyMaps(saveImage=False, catalogRegions="2AGL", catalogRegionsColor="red")
        for m in maps:
            self.assertEqual(True, os.path.isfile(m))

        ag.destroy()
    """

    def test_calc_bkg(self):

        ag = AGAnalysis(self.agilepyconfPath, self.sourcesconfPathcalcBkg)

        ag.setOptions(   tmin=456461778.0,
                         tmax=456537945.0,
                         timetype="TT",
                         galcoeff=[-1, -1, -1, -1],
                         isocoeff=[10, 12, 10, 12]
                     )

        galBkg, isoBkg, maplistfile = ag.calcBkg('CYGX3', pastTimeWindow=0)

        print("\ngalBkg:",galBkg)
        print("isoBkg:",isoBkg)

        galBkg, isoBkg, maplistfile = ag.calcBkg('CYGX3', galcoeff=[-1,-1,-1,-1], pastTimeWindow=0)
        print("\ngalBkg:",galBkg)
        print("isoBkg:",isoBkg)


        galBkg, isoBkg, maplistfile = ag.calcBkg('CYGX3', galcoeff=[0,0,0,0], pastTimeWindow=0)
        print("\ngalBkg:",galBkg)
        print("isoBkg:",isoBkg)


        galBkg, isoBkg, maplistfile = ag.calcBkg('CYGX3', galcoeff=[0.8, 0.6, 0.8, 0.6], pastTimeWindow=0)
        print("\ngalBkg:",galBkg)
        print("isoBkg:",isoBkg)

        ag.destroy()


if __name__ == '__main__':
    unittest.main()
