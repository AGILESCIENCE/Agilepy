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

        self.VELA = "2AGLJ0835-4514"
        self.sourcesConfTxt = os.path.join(self.currentDirPath,"conf/sourcesconf_1.txt")
        self.sourcesConfXml = os.path.join(self.currentDirPath,"conf/sourcesconf_1.xml")
        self.agilepyConf = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        outDir = Path(os.path.join(os.environ["AGILE"])).joinpath("agilepy-test-data/unittesting-output/api")
        if outDir.exists() and outDir.is_dir():
            shutil.rmtree(outDir)

    def test_delete_output_directory(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        outDir = Path(ag.getOption("outdir"))

        self.assertEqual(True, outDir.exists() and outDir.is_dir())

        ag.deleteAnalysisDir()

        self.assertEqual(False, outDir.exists())

    def test_generate_maps(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        outDir = ag.getOption("outdir")

        maplistFilePath = ag.generateMaps()
        self.assertEqual(True, os.path.isfile(maplistFilePath))

        maps = os.listdir(Path(outDir).joinpath("maps"))
        self.assertEqual(16, len(maps))

        lines = None
        with open(maplistFilePath) as mfp:
            lines = mfp.readlines()

        self.assertEqual(4, len(lines))

        ag.destroy()

    def test_update_gal_iso(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        outDir = Path(ag.getOption("outdir"))

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
        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        maplistFilePath = ag.generateMaps()
        self.assertEqual(True, os.path.isfile(maplistFilePath))

        products_1 = ag.mle(maplistFilePath)
        for p in products_1:
            self.assertEqual(True, os.path.isfile(p))

        products_2 = ag.mle(maplistFilePath)
        for p in products_2:
            self.assertEqual(True, os.path.isfile(p))

        ag.destroy()

    def test_source_dist_updated_after_source_position_update(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        source_1 = ag.selectSources(lambda name: name == self.VELA).pop()
        dist_1 = source_1.spatialModel.get("dist")

        ag.updateSourcePosition(self.VELA, glon=264, glat=-3)

        source_2 = ag.selectSources(lambda name: name == self.VELA).pop()
        dist_2 = source_2.spatialModel.get("dist")

        self.assertNotEqual(dist_1, dist_2)
        ag.destroy()

    def test_source_dist_updated_after_mle(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        maplistFilePath = ag.generateMaps()

        ag.freeSources(lambda name: name == self.VELA, "pos", True)
        ag.freeSources(lambda name: name == self.VELA, "flux", True)

        source = ag.selectSources(lambda name: name == self.VELA).pop()
        dist_before = source.spatialModel.get("dist")

        ag.mle(maplistFilePath)

        source = ag.selectSources(lambda name: name == self.VELA).pop()
        dist_after = source.spatialModel.get("dist")
        multiDist_after = source.multi.get("multiDist")

        self.assertNotEqual(dist_before, dist_after)
        self.assertEqual(multiDist_after, dist_after)

        ag.destroy()

    def test_source_flux_updated_after_mle(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        maplistFilePath = ag.generateMaps()

        ag.freeSources(lambda name: name == self.VELA, "flux", True)

        source_1 = ag.selectSources(lambda name: name == self.VELA).pop()
        
        flux_1 = source_1.spectrum.get("flux")

        ag.mle(maplistFilePath)

        source_2 = ag.selectSources(lambda name: name == self.VELA).pop()
        flux_2 = source_2.multi.get("multiFlux")

        self.assertNotEqual(flux_1, flux_2)

        ag.destroy()

    def test_parse_maplistfile(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

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

    def test_saving_sky_maps(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)
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

    def test_saving_sky_maps_singlemode(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)
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

    def test_lc(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        ag.setOptions(energybins=[[100, 300]], fovbinnumber=1) # to reduce the computational time

        ag.freeSources(lambda name: name == self.VELA, "flux", True)

        lightCurveData = ag.lightCurveMLE(self.VELA, tmin=433857532, tmax=433900000, timetype="TT", binsize=20000)

        self.assertEqual(True, os.path.isfile(lightCurveData))

        lightCurvePlot = ag.displayLightCurve("mle", saveImage=True)

        self.assertEqual(True, os.path.isfile(lightCurvePlot))

        # ag.destroy()

    def test_simple_lc(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        ag.setOptions(energybins=[[100, 300]], fovbinnumber=1) # to reduce the computational time

        ag.freeSources(lambda name: name == self.VELA, "flux", True)

        lightCurveData = ag.aperturePhotometry()[0]

        self.assertEqual(True, os.path.isfile(lightCurveData))

        lightCurvePlot = ag.displayLightCurve("ap", saveImage=True)

        self.assertEqual(True, os.path.isfile(lightCurvePlot))

        ag.destroy()

    def test_calc_bkg(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        ag.setOptions(  timetype="TT",
                        galcoeff=[-1, -1, -1, -1],
                        isocoeff=[10, 12, 10, 12]
                     )

        """
        galBkg, isoBkg, maplistfile = ag.calcBkg('CYGX3', pastTimeWindow=0)
        print("\ngalBkg:",galBkg)
        print("isoBkg:",isoBkg)

        galBkg, isoBkg, maplistfile = ag.calcBkg('CYGX3', galcoeff=[-1,-1,-1,-1], pastTimeWindow=0)
        print("\ngalBkg:",galBkg)
        print("isoBkg:",isoBkg)


        galBkg, isoBkg, maplistfile = ag.calcBkg('CYGX3', galcoeff=[0,0,0,0], pastTimeWindow=0)
        print("\ngalBkg:",galBkg)
        print("isoBkg:",isoBkg)
        """

        galCoeff, isoCoeff, maplistfile = ag.calcBkg(self.VELA, galcoeff=[0.8, 0.6, 0.8, 0.6], pastTimeWindow=0)
       
        self.assertEqual([10, 12, 10, 12], isoCoeff)
        self.assertEqual([0.8, 0.6, 0.8, 0.6], galCoeff)

        ag.destroy()

    def test_extract_light_curve_data(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        sourceFile = Path(self.currentDirPath).joinpath("data/testcase_2AGLJ0835-4514.source")

        lcdata = ag._extractLightCurveDataFromSourceFile(str(sourceFile))

        lcdataKeys = ['sqrt(ts)', 'flux', 'flux_err', 'flux_ul', 'gal', 'iso', 'l_peak', 'b_peak', 'dist_peak', 'l', 'b', 'r', 'dist', 'time_start_tt', 'time_end_tt']

        for key in lcdataKeys:
            self.assertEqual(True, key in lcdata)

        ag.destroy()

    def test_fix_exponent(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        self.assertEqual('894.587e-08', ag._fixToNegativeExponent(8.94587e-06, fixedExponent=-8))
        self.assertEqual('309.757e-08', ag._fixToNegativeExponent(3.09757e-06, fixedExponent=-8))
        self.assertEqual('1623.16e-08', ag._fixToNegativeExponent(1.62316e-05, fixedExponent=-8))
        self.assertEqual('1.524e-08', ag._fixToNegativeExponent(1.524e-8, fixedExponent=-8))
        self.assertEqual('1.524e+18e-08', ag._fixToNegativeExponent(1.524e10, fixedExponent=-8))
        self.assertEqual('0.0', ag._fixToNegativeExponent(0.0, fixedExponent=-8))

        ag.destroy()

    def test_aperture_photometry(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        outDir = ag.getOption("outdir")

        ap_file, ap_ph_file = ag.aperturePhotometry()
        
        self.assertEqual(True, os.path.isfile(ap_file))

        # the second product is not produced in this case
        self.assertEqual(None, ap_ph_file) 

        ag.destroy()

    def test_update_source_parameter_value(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        sources = ag.selectSources(lambda name: name == self.VELA)
        
        source = sources.pop()

        self.assertEqual(1.34774, source.spectrum.get("index2"))
        source.spectrum.set("index2", 1)
        self.assertEqual(1, source.spectrum.get("index2"))

        self.assertEqual(969.539e-08, source.spectrum.get("flux"))
        source.spectrum.set("flux", 1)
        self.assertEqual(1, source.spectrum.get("flux"))

        self.assertEqual(3913.06, source.spectrum.get("cutoffEnergy"))
        source.spectrum.set("cutoffEnergy", 1)
        self.assertEqual(1, source.spectrum.get("cutoffEnergy"))

        self.assertRaises(AttributeError, source.spectrum.get, "index")
        self.assertRaises(AttributeError, source.spectrum.set, "index", 10)

        ag.destroy()

    def test_multi_update_free_parameters(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        ag.generateMaps()

        sources = ag.selectSources(lambda name: name == self.VELA)

        source = sources.pop()

        #index2 = source.spectrum.get("index2")
        flux = source.spectrum.get("flux")
        #cutoffEnergy = source.spectrum.get("cutoffEnergy") 

        ag.freeSources(lambda name: name == self.VELA, "pos", True)
        # ag.freeSources(lambda name: name == self.VELA, "index2", True)
        ag.freeSources(lambda name: name == self.VELA, "flux", True)
        # ag.freeSources(lambda name: name == self.VELA, "cutoffEnergy", True)

        ag.mle()

        self.assertEqual(True, source.multi.get("multiFlux") == source.spectrum.get("flux"))
        self.assertEqual(True, flux != source.spectrum.get("flux"))

        #todo: validation test 

        ag.destroy()

    def test_print_source(self):

        ag = AGAnalysis(self.agilepyConf, self.sourcesConfTxt)

        sources = ag.selectSources(lambda name: name == self.VELA)

        for s in sources:
            self.assertEqual(True, len(str(s))>370)
            print(s)


if __name__ == '__main__':
    unittest.main()
