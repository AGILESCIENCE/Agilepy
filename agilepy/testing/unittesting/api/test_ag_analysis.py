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
import pytest
from pathlib import Path
from pytest import approx

from agilepy.api.AGAnalysis import AGAnalysis
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.CustomExceptions import (
    SourceModelFormatNotSupported, 
    MaplistIsNone, 
    SourcesLibraryIsEmpty, 
    ValueOutOfRange, 
    ConfigurationsNotValidError, 
    CannotSetNotUpdatableOptionError
)

class TestAGAnalysis:

    VELA = "2AGLJ0835-4514"

    @pytest.mark.testlogsdir("api/test_logs/test_delete_output_directory")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_delete_output_directory(self, logger, config, testdatafiles):

        ag = AGAnalysis(config, testdatafiles[0])

        outDir = Path(ag.getOption("outdir"))

        assert outDir.exists() and outDir.is_dir()

        ag.deleteAnalysisDir()

        assert not outDir.exists()


    ########################################################################
    # test_generate_maps
    ########################################################################
    def assert_maplistfile_lines_number(self, maplistFilePath, numberOfLines):
        assert Path(maplistFilePath).is_file()
        with open(maplistFilePath) as mfp:
            lines = mfp.readlines()
            assert numberOfLines == len(lines)

    def assert_generated_maps_number(self, outDir, numberOfMaps):
        maps = [map for map in os.listdir(outDir) if ".gz" in map]
        assert numberOfMaps == len(maps)

    def assert_generated_maps_exist(self, skyMapMatrix):
        for skyMapRow in skyMapMatrix:
            assert Path(skyMapRow[0]) #cts
            assert Path(skyMapRow[1]) #exp
            assert Path(skyMapRow[2]) #gas


    @pytest.mark.testlogsdir("api/test_logs/test_generate_maps")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_generate_maps(self, logger, config, testdatafiles):

        ag = AGAnalysis(config, testdatafiles[0])

        ag.setOptions(tmin=433857532, tmax=433858532, timetype="TT")

        outDir = ag.getOption("outdir")

        maplistFilePath0 = ag.generateMaps()
        self.assert_maplistfile_lines_number(maplistFilePath0, 4)
        outDir0 = Path(outDir).joinpath("maps", "0")
        assert outDir0.is_dir()
        self.assert_generated_maps_number(outDir0, 16)
        self.assert_generated_maps_exist(ag.parseMaplistFile(maplistFilePath0))

        # second generation (same parameters)
        maplistFilePath1 = ag.generateMaps()
        self.assert_maplistfile_lines_number(maplistFilePath1, 4)
        outDir1 = Path(outDir).joinpath("maps", "1")
        assert outDir1.is_dir()
        self.assert_generated_maps_number(outDir1, 16)
        self.assert_generated_maps_exist(ag.parseMaplistFile(maplistFilePath1))

        
        # third generation with different time interval
        ag.setOptions(tmin=433957532, tmax=433957632, timetype="TT")
        maplistFilePath2 = ag.generateMaps()
        self.assert_maplistfile_lines_number(maplistFilePath2, 4)
        outDir2 = Path(outDir).joinpath("maps", "2")
        assert outDir2.is_dir()     
        self.assert_generated_maps_number(outDir2, 16)
        self.assert_generated_maps_exist(ag.parseMaplistFile(maplistFilePath2))

        # fourth generation with different glon and glat
        ag.setOptions(glon=265, glat=-3, timetype="TT")
        maplistFilePath3 = ag.generateMaps()
        self.assert_maplistfile_lines_number(maplistFilePath3, 4)
        outDir3 = Path(outDir).joinpath("maps", "3")
        assert outDir3.is_dir()
        self.assert_generated_maps_number(outDir3, 16)
        self.assert_generated_maps_exist(ag.parseMaplistFile(maplistFilePath3))


        # fifth generation with different fovbinnumber, and energy range
        ag.setOptions(fovbinnumber=1, energybins=[[100,300]])
        maplistFilePath4 = ag.generateMaps()
        self.assert_maplistfile_lines_number(maplistFilePath4, 1)
        outDir3 = Path(outDir).joinpath("maps", "4")
        assert outDir3.is_dir()       
        self.assert_generated_maps_number(outDir3, 4)
        self.assert_generated_maps_exist(ag.parseMaplistFile(maplistFilePath4))

        ag.destroy()
        
    @pytest.mark.testlogsdir("api/test_logs/test_update_gal_iso")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_update_gal_iso(self, logger, config, testdatafiles):        

        ag = AGAnalysis(config, testdatafiles[0])

        ag.setOptions(tmin=433857532, tmax=433858532, timetype="TT")

        outDir = Path(ag.getOption("outdir"))

        ag.config.setOptions(galcoeff=[0.6, 0.8, 0.6, 0.8])
        ag.config.setOptions(isocoeff=[10, 15, 10, 15])

        galcoeffs = ag.config.getOptionValue("galcoeff")
        isocoeffs = ag.config.getOptionValue("isocoeff")

        _ = ag.generateMaps()

        matrix = ag.parseMaplistFile()
        for idx, row in enumerate(matrix):
            assert str(galcoeffs[idx]) == row[4]
            assert str(isocoeffs[idx]) == row[5]


        ag.config.setOptions(galcoeff=[0,0,0,0])
        ag.config.setOptions(isocoeff=[0,0,0,0])

        galcoeffs = ag.config.getOptionValue("galcoeff")
        isocoeffs = ag.config.getOptionValue("isocoeff")

        matrix = ag.parseMaplistFile()
        for idx, row in enumerate(matrix):
            assert str(galcoeffs[idx]) == row[4]
            assert str(isocoeffs[idx]) == row[5]

        # ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_mle")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    def test_mle(self, logger, config):

        ag = AGAnalysis(config)
        ag.setOptions(tmin = 433857532, tmax = 433858532, timetype = "TT", glon = 263.55, glat = -2.78)
        with pytest.raises(MaplistIsNone):
            ag.mle()
        ag.generateMaps()
        with pytest.raises(SourcesLibraryIsEmpty):
            ag.mle()


    @pytest.mark.testlogsdir("api/test_logs/test_analysis_pipeline")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_analysis_pipeline(self, logger, config, testdatafiles): 

        ag = AGAnalysis(config, testdatafiles[0])

        ag.setOptions(tmin = 433857532, tmax = 434289532, timetype = "TT", glon = 263.55, glat = -2.78)
        maplistFilePath = ag.generateMaps()
        assert os.path.isfile(maplistFilePath)

        sources = ag.loadSourcesFromCatalog("2AGL", rangeDist = (0, 21))
        sources = ag.freeSources('name == "2AGLJ0835-4514"', "flux", True, show=True)

        products_1 = ag.mle()

        for p in products_1:
            assert os.path.isfile(p)

        products_2 = ag.mle()
        for p in products_2:
            assert os.path.isfile(p)

        ag.setOptions(tmin = 433857532, tmax = 433907532, timetype = "TT", glon = 263.55, glat = -2.78)

        maplistfile = ag.generateMaps()
        
        products_3 = ag.mle()
        for p in products_3:
            assert os.path.isfile(p)
        
        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_source_dist_updated_after_source_position_update")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_source_dist_updated_after_source_position_update(self, logger, config, testdatafiles): 

        ag = AGAnalysis(config,testdatafiles[0] )
        ag.setOptions(tmin = 433857532, tmax = 433857542, timetype = "TT", fovbinnumber=1, energybins=[[100,200]], glon = 263.55, glat = -2.78)

        source_1 = ag.selectSources(lambda name: name == TestAGAnalysis.VELA ).pop()
        dist_1 = source_1.spatialModel.get("dist")["value"]

        ag.updateSourcePosition(TestAGAnalysis.VELA , glon=264, glat=-3)

        source_2 = ag.selectSources(lambda name: name == TestAGAnalysis.VELA ).pop()
        dist_2 = source_2.spatialModel.get("dist")["value"]

        assert True, dist_1 != dist_2
        ag.destroy()


    @pytest.mark.testlogsdir("api/test_logs/test_source_dist_updated_after_mle")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_source_dist_updated_after_mle(self, logger, config, testdatafiles): 
    
        ag = AGAnalysis(config,testdatafiles[0] )

        maplistFilePath = ag.generateMaps()

        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "pos", True)
        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "flux", True)

        source = ag.selectSources(lambda name: name == TestAGAnalysis.VELA ).pop()
        print(source)
        dist_before = source.get("dist")["value"]

        ag.mle(maplistFilePath)

        source = ag.selectSources(lambda name: name == TestAGAnalysis.VELA ).pop()
        print(source)
        dist_after = source.get("dist")["value"]
        multiDist_after = source.get("multiDist")["value"]

        assert dist_before == dist_after
        assert multiDist_after != dist_after

        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_source_flux_updated_after_mle")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_source_flux_updated_after_mle(self, logger, config, testdatafiles): 

        ag = AGAnalysis(config,testdatafiles[0] )

        maplistFilePath = ag.generateMaps()

        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "flux", True)

        source_1 = ag.selectSources(lambda name: name == TestAGAnalysis.VELA ).pop()
        
        flux_1 = source_1.get("flux")["value"]

        ag.mle(maplistFilePath)

        source_2 = ag.selectSources(lambda name: name == TestAGAnalysis.VELA ).pop()
        flux_2 = source_2.get("multiFlux")["value"]

        assert flux_1 != flux_2

        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_parse_maplistfile")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_parse_maplistfile(self, logger, config, testdatafiles): 

        ag = AGAnalysis(config,testdatafiles[0])

        ag.setOptions(energybins=[[100,300],[300,1000]], fovbinnumber=2)
        maplistFilePath = ag.generateMaps()

        maplistRows1 = ag.parseMaplistFile()
        maplistRows2 = ag.parseMaplistFile(maplistFilePath)

        assert 4 == len(maplistRows1)
        assert 4 == len(maplistRows2)

        for i in range(4):
            for j in range(3):
                assert maplistRows1[i][j], maplistRows2[i][j]

        for i in range(4):
            for j in range(3):
                assert os.path.isfile(maplistRows1[i][j])

        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_saving_sky_maps")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_saving_sky_maps(self, logger, config, testdatafiles): 

        ag = AGAnalysis(config,testdatafiles[0] )
        ag.setOptions(tmin = 433857532, tmax = 433857732, timetype = "TT")
        _ = ag.generateMaps()

        maps = ag.displayCtsSkyMaps(singleMode=False, saveImage=True)
        for m in maps:
            assert os.path.isfile(m)

        maps = ag.displayExpSkyMaps(singleMode=False, saveImage=True)
        for m in maps:
            assert os.path.isfile(m)

        maps = ag.displayGasSkyMaps(singleMode=False, saveImage=True)
        for m in maps:
            assert os.path.isfile(m)

        ag.destroy()



    @pytest.mark.testlogsdir("api/test_logs/test_saving_sky_maps_singlemode")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_saving_sky_maps_singlemode(self, logger, config, testdatafiles):

        ag = AGAnalysis(config,testdatafiles[0] )
        _ = ag.generateMaps()

        maps = ag.displayCtsSkyMaps(saveImage=True)
        for m in maps:
            assert os.path.isfile(m)

        maps = ag.displayExpSkyMaps(saveImage=True)
        for m in maps:
            assert os.path.isfile(m)

        maps = ag.displayGasSkyMaps(saveImage=True)
        for m in maps:
            assert os.path.isfile(m)

        ag.destroy()


    @pytest.mark.testlogsdir("api/test_logs/test_lc")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_lc(self, logger, config, testdatafiles):

        ag = AGAnalysis(config,testdatafiles[0] )

        ag.setOptions(energybins=[[100, 300]], fovbinnumber=1) # to reduce the computational time

        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "flux", True)

        lightCurveData = ag.lightCurveMLE(TestAGAnalysis.VELA , tmin=433860000, tmax=433880000, timetype="TT", binsize=20000)

        assert os.path.isfile(lightCurveData)

        with open(lightCurveData, "r") as lcd:
            lines = lcd.readlines()
            # print("readlines: ", lines)
        assert len(lines) == 1+1 # 1 header + 2 temporal bins

        lightCurveData = ag.lightCurveMLE(TestAGAnalysis.VELA , tmin=433900000, tmax=433940000, timetype="TT", binsize=20000)

        assert os.path.isfile(lightCurveData)

        with open(lightCurveData, "r") as lcd:
            lines = lcd.readlines()
            # print("readlines: ", lines)
        assert len(lines) == 3 # 1 header + 2 temporal bins

        lightCurvePlot = ag.displayLightCurve("mle", saveImage=True)
        assert os.path.isfile(lightCurvePlot)

        ag.destroy()

    """def test_simple_lc(self):

        ag = AGAnalysis(config,testdatafiles[0] )

        ag.setOptions(energybins=[[100, 300]], fovbinnumber=1) # to reduce the computational time

        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "flux", True)

        lightCurveData = ag.aperturePhotometry()[0]

        assert os.path.isfile(lightCurveData))

        lightCurvePlot = ag.displayLightCurve("ap", saveImage=True)

        assert os.path.isfile(lightCurvePlot))

        ag.destroy()"""

    @pytest.mark.testlogsdir("api/test_logs/test_generic_column")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_generic_column(self, logger, config, testdatafiles):
        
        ag = AGAnalysis(config,testdatafiles[0] )

        ag.setOptions(energybins=[[100, 300]], fovbinnumber=1)

        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "flux", True)

        lightCurveData = ag.lightCurveMLE(
            TestAGAnalysis.VELA , tmin=433860000, tmax=433880000, timetype="TT", binsize=20000)

        #filename = ag.displayGenericColumns(
        #    lightCurveData, columns=["l_peak"], um=["test_um"], saveImage=True)

        filename = ag.displayGenericColumns(
            lightCurveData, columns=["l_peak", "counts"], um=["test_um", "counts"], saveImage=True)

        assert os.path.isfile(filename)

        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_calc_bkg")
    @pytest.mark.testconfig("api/conf/agilepyconfbkg.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_calc_bkg(self, logger, config, testdatafiles):

        ag = AGAnalysis(config, testdatafiles[0])

        # First test: coeffs are fixed in the configuration files, galcoeff is not passed
        ag.setOptions(energybins=[[100, 300], [300, 1000]], fovbinnumber=2)
        ag.setOptions(galcoeff=[0.6, 0.8, 0.6, 0.8], isocoeff=[10, 15, 10, 15])
        galCoeff, isoCoeff, maplistfile = ag.calcBkg(TestAGAnalysis.VELA , pastTimeWindow=0)
        print("first test:", galCoeff, isoCoeff)
        expectedGal = [0.650145, 0.687911, 0.105915, 0.161874] 
        expectedIso = [2.06451, 2.48712, 12.0703, 3.60618]
        

        for i in range(3):
            assert galCoeff[i] == approx(expectedGal[i],  rel=1e-3, abs=1e-3)
            assert isoCoeff[i] == approx(expectedIso[i],  rel=1e-3, abs=1e-3)
        
        # Second test: coeffs are fixed in the configuration files, galcoeff is passed
        galCoeff, isoCoeff, maplistfile = ag.calcBkg(TestAGAnalysis.VELA , galcoeff=[0.6, 0.8, 0.6, 0.8], pastTimeWindow=0)
        print("second test:", galCoeff, isoCoeff)
        expectedGal = [0.6, 0.8, 0.6, 0.8]
        expectedIso = [2.58443, 2.15484, 7.29793, 1.41975]
        


        for i in range(3):
            assert galCoeff[i] == approx(expectedGal[i],  rel=1e-3, abs=1e-3)
            assert isoCoeff[i] == approx(expectedIso[i],  rel=1e-3, abs=1e-3)
        # The configuration file has been updated

        #third test: deprecated
        
        
        # Fourth test: change the past window
        galCoeff, isoCoeff, maplistfile = ag.calcBkg(TestAGAnalysis.VELA , pastTimeWindow=0)
        expectedGal = [0.650145, 0.687911, 0.105915, 0.161874]
        expectedIso = [2.06451, 2.48712, 12.0703, 3.60618]
        print("fourth test:", galCoeff, isoCoeff)


        for i in range(3):
            assert galCoeff[i] == approx(expectedGal[i],  rel=1e-3, abs=1e-3)
            assert isoCoeff[i] == approx(expectedIso[i],  rel=1e-3, abs=1e-3)

        ag.setOptions(galcoeff=[-1, -1, -1, -1], isocoeff=[-1, -1, -1, -1])
        galCoeff, isoCoeff, maplistfile = ag.calcBkg(TestAGAnalysis.VELA , pastTimeWindow=2)
        print("fourth test at -1:", galCoeff, isoCoeff)
        
        
        assert galCoeff != expectedGal
        assert isoCoeff != expectedIso
        
        #fifth test: using excludeTminTmax
        galCoeff, isoCoeff, maplistfile = ag.calcBkg(TestAGAnalysis.VELA , pastTimeWindow=2, excludeTmaxTmin=True)
        expectedGal = [0.390775, 0.0514248, 6.27864e-09, 0.704969] 
        expectedIso = [2.84136, 1.98057, 9.81532, 1.33809]
        print("fifth test", galCoeff, isoCoeff)

        for i in range(3):
            assert galCoeff[i] == approx(expectedGal[i],  rel=1e-3, abs=1e-3)
            assert isoCoeff[i] == approx(expectedIso[i],  rel=1e-3, abs=1e-3)
        
        ag.destroy()


    @pytest.mark.testlogsdir("api/test_logs/test_extract_light_curve_data")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt", "api/data/testcase_2AGLJ0835-4514.source"])
    def test_extract_light_curve_data(self, logger, config, testdatafiles):

        ag = AGAnalysis(config,testdatafiles[0] )

        sourceFile = testdatafiles[1]

        lcdata = ag._extractLightCurveDataFromSourceFile(str(sourceFile))


        lcdataKeys = ["sqrt(ts)", "flux","flux_err", "flux_ul","gal","gal_error","iso","iso_error",\
            "l_peak","b_peak","dist_peak","l","b","r","ell_dist","a","b","phi","exp","ExpRatio","counts",\
            "counts_err","Index","Index_Err","Par2","Par2_Err","Par3","Par3_Err","Erglog","Erglog_Err","Erglog_UL",\
            "time_start_tt","time_end_tt","Fix","index","ULConfidenceLevel","SrcLocConfLevel","start_l","start_b",\
            "start_flux","typefun","par2","par3","galmode2","isomode2","isomode2fit","edpcor","fluxcor",\
            "integratortype","expratioEval","expratio_minthr","expratio_maxthr","expratio_size",\
            "emin", "emax", "fovmin", "fovmax", "albedo", "binsize", "expstep", "phasecode", "fit_cts", \
            "fit_fitstatus0", "fit_fcn0", "fit_edm0", "fit_nvpar0", "fit_nparx0", "fit_iter0", \
            "fit_fitstatus1", "fit_fcn1", "fit_edm1", "fit_nvpar1", "fit_nparx1", "fit_iter1", "fit_Likelihood1"]

        assert len(lcdataKeys) == len(lcdata)
        
        for key in lcdataKeys:
            assert key in lcdata

        ag.destroy()


    @pytest.mark.testlogsdir("api/test_logs/test_fix_exponent")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_fix_exponent(self, logger, config, testdatafiles):

        ag = AGAnalysis(config,testdatafiles[0] )

        assert '894.587e-08' == ag._fixToNegativeExponent(8.94587e-06, fixedExponent=-8)
        assert '309.757e-08' == ag._fixToNegativeExponent(3.09757e-06, fixedExponent=-8)
        assert '1623.16e-08' == ag._fixToNegativeExponent(1.62316e-05, fixedExponent=-8)
        assert '1.524e-08'   == ag._fixToNegativeExponent(1.524e-8, fixedExponent=-8)
        assert '1.524e+18e-08' == ag._fixToNegativeExponent(1.524e10, fixedExponent=-8)
        assert '0.0'         == ag._fixToNegativeExponent(0.0, fixedExponent=-8)

        ag.destroy()

    @pytest.mark.skip("Fails on MACOS")
    @pytest.mark.testlogsdir("api/test_logs/test_aperture_photometry")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_aperture_photometry(self, logger, config, testdatafiles):    

        ag = AGAnalysis(config,testdatafiles[0] )

        outDir = ag.getOption("outdir")

        ap_file, ap_ph_file = ag.aperturePhotometry()
        
        assert os.path.isfile(ap_file)

        # the second product is not produced in this case
        assert ap_ph_file is None 

        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_update_source_parameter_value")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_update_source_parameter_value(self, logger, config, testdatafiles): 

        ag = AGAnalysis(config,testdatafiles[0] )

        sources = ag.selectSources(lambda name: name == TestAGAnalysis.VELA )
        
        source = sources.pop()

        assert 1.34774 == source.spectrum.getVal("index2")
        source.set("index2", {"value": 1})
        assert 1 == source.spectrum.getVal("index2")

        assert 969.539e-08 == source.spectrum.getVal("flux")
        source.set("flux", {"value": 1})
        assert 1 == source.spectrum.getVal("flux")

        assert 3913.06 == source.spectrum.getVal("cutoffEnergy")
        source.set("cutoffEnergy", {"value": 1})
        assert 1 == source.spectrum.getVal("cutoffEnergy")

        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_multi_update_free_parameters")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_multi_update_free_parameters(self, logger, config, testdatafiles): 

        ag = AGAnalysis(config,testdatafiles[0] )

        ag.generateMaps()

        sources = ag.selectSources(lambda name: name == TestAGAnalysis.VELA )

        source = sources.pop()

        #index2 = source.spectrum.get("index2")
        flux = source.spectrum.getVal("flux")
        #cutoffEnergy = source.spectrum.get("cutoffEnergy") 

        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "pos", True)
        # ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "index2", True)
        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "flux", True)
        # ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "cutoffEnergy", True)
        print(source)

        ag.mle()

        print(source)

        assert source.multiAnalysis.getVal("multiFlux") != source.spectrum.getVal("flux")
        assert flux == source.spectrum.getVal("flux")

        ag.mle()

        assert source.multiAnalysis.getVal("multiFlux") != source.spectrum.getVal("flux")
        assert flux != source.spectrum.getVal("flux")

        print(source)

        #todo: validation test 

        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_print_source")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    @pytest.mark.testdatafiles(["api/conf/sourcesconf_1.txt"])
    def test_print_source(self, logger, config, testdatafiles): 

        ag = AGAnalysis(config,testdatafiles[0] )

        sources = ag.selectSources(lambda name: name == TestAGAnalysis.VELA )

        for s in sources:
            assert len(str(s))>370
            print(s)

    @pytest.mark.testlogsdir("api/test_logs/test_write_sources_on_file")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    def test_write_sources_on_file(self, logger, config): 

        ag = AGAnalysis(config)

        sources_subset = ag.loadSourcesFromCatalog("2AGL", rangeDist=(0, 30))

        with pytest.raises(SourceModelFormatNotSupported):
            ag.writeSourcesOnFile("regfile", "notsupportedformat", sources_subset)

        #reg
        regfile = ag.writeSourcesOnFile("regfile", "reg", sources_subset)    
        with open(regfile) as f:
            linesNum = sum(1 for line in f)
        assert 1 == linesNum
        
        """
        ag.generateMaps()
        ag.mle()
        regfile = ag.writeSourcesOnFile("regfile", "reg", sources_subset)    
        with open(regfile) as f:
            linesNum = sum(1 for line in f)
        assert len(sources_subset)+1, linesNum)
        """

        ag.generateMaps()
        ag.freeSources(lambda name: name == TestAGAnalysis.VELA , "pos", True)
        ag.mle()
        regfile = ag.writeSourcesOnFile("regfile", "reg", sources_subset)    
        with open(regfile) as f:
            linesNum = sum(1 for line in f)
        assert len(sources_subset)+1 == linesNum

    @pytest.mark.testlogsdir("api/test_logs/test_setOptionTimeMJD")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    def test_setOptionTimeMJD(self, logger, config): 
        
        ag = AGAnalysis(config)

        tmin1 = 58030.0
        tmax1 = 58035.0

        tmintt = AstroUtils.time_mjd_to_agile_seconds(tmin1)
        tmaxtt = AstroUtils.time_mjd_to_agile_seconds(tmax1)

        ag.setOptionTimeMJD(tmin=tmin1, tmax=tmax1)

        tmin2 = ag.getOption("tmin")

        tmax2 = ag.getOption("tmax")

        assert tmintt == tmin2
        assert tmaxtt == tmax2

        ag.destroy()


    @pytest.mark.testlogsdir("api/test_logs/test_setOptionEnergybin")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    def test_setOptionEnergybin(self, logger, config): 
        
        ag = AGAnalysis(config)

        energybin0 = [[100, 10000]]
        energybin1 = [[100, 50000]]
        energybin2 = [[100, 300], [300, 1000], [1000, 3000], [3000, 10000]]
        energybin3 = [[100, 300], [300, 1000], [1000, 3000], [3000, 10000], [10000, 50000]]
        energybin4 = [[50, 100], [100, 300], [300, 1000], [1000, 3000], [3000, 10000]]
        energybin5 = [[50, 100], [100, 300], [300, 1000], [1000, 3000], [3000, 10000], [10000, 50000]]

        with pytest.raises(ValueOutOfRange):
            ag.setOptionEnergybin(42)

        ag.setOptionEnergybin(0)
        assert ag.getOption("energybins") == energybin0

        ag.setOptionEnergybin(1)
        assert ag.getOption("energybins") == energybin1

        ag.setOptionEnergybin(2)
        assert ag.getOption("energybins") == energybin2

        ag.setOptionEnergybin(3)
        assert ag.getOption("energybins") == energybin3

        ag.setOptionEnergybin(4)
        assert ag.getOption("energybins") == energybin4

        ag.setOptionEnergybin(5)
        assert ag.getOption("energybins") == energybin5

        ag.destroy()
    

    @pytest.mark.testlogsdir("api/test_logs/test_setDQ")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    def test_setDQ(self, logger, config):

        ag = AGAnalysis(config)

        # dq out of range
        with pytest.raises(ConfigurationsNotValidError):
            ag.setOptions(dq=42)

        # dq = 0
        ag.setOptions(dq=0, albedorad=101, fovradmax=102)
        assert ag.getOption("albedorad") == 101
        assert ag.getOption("fovradmax") == 102

        # dq == 5 
        ag.setOptions(dq=5)
        assert ag.getOption("albedorad") == 100
        assert ag.getOption("fovradmax") == 50
        
        # Try to change albedorad or fovradmax with dq == 5
        with pytest.raises(CannotSetNotUpdatableOptionError):
            ag.setOptions(albedorad=42, fovradmax=42)        


        ag.destroy()

    @pytest.mark.testlogsdir("api/test_logs/test_fixed_parameters")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    def test_fixed_parameters(self, logger, config):

        ag = AGAnalysis(config)

        ag.setOptions(
            energybins=[[100, 1000]], tmin=434279000,
            tmax=434289532,
            timetype="TT")

        sources = ag.loadSourcesFromCatalog("2AGL", rangeDist=(0, 25))
        
        assert len(sources) == 9

        source = ag.selectSources('name == "2AGLJ0835-4514"').pop()

        flux0 = source.spectrum.getVal("flux")
        
        sources = ag.freeSources(
            'name == "2AGLJ0835-4514"', "flux", False, show=True)

        _ = ag.generateMaps()

        _ = ag.mle()
        
        flux1 = source.get("multiFlux")["value"]

        assert flux0 == approx(flux1,  rel=1e-9, abs=1e-9)


        ag.destroy()
    

    @pytest.mark.testlogsdir("api/test_logs/test_get_analysis_dir")
    @pytest.mark.testconfig("api/conf/agilepyconf.yaml")
    def test_get_analysis_dir(self, logger, config):
            
        ag = AGAnalysis(config)

        outdir = ag.getAnalysisDir()

        outdir = Path(outdir)

        assert outdir.is_dir() and outdir.exists()

