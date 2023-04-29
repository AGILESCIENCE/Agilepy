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

class TestSourcesLibrary:

    @staticmethod
    def get_free_params(source):

        return {
                 "curvature": source.spectrum.curvature["free"],
                 "pivot_energy": source.spectrum.pivotEnergy["free"],
                 "index": source.spectrum.index["free"],
                 "pos": source.spatialModel.pos["free"],
                 "flux": source.spectrum.flux["free"]
               }


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sourceconf.wrongext")
    def test_load_file_with_wrong_extension(self, configObject, logger, testdata):

        sl = SourcesLibrary(configObject, logger)

        with pytest.raises(SourceModelFormatNotSupported):
            sl.loadSourcesFromFile(testdata)


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sourceconf.idontexitst.txt")
    def test_load_wrong_file(self, configObject, logger, testdata):
        logger.info(f"Hello! {AgilepyLogger().getRootLogsDir()}")

        sl = SourcesLibrary(configObject, logger)

        with pytest.raises(FileNotFoundError):
            sl.loadSourcesFromFile(testdata)


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    def test_load_from_catalog(self, configObject, logger):
        sl = SourcesLibrary(configObject, logger)

        added = sl.loadSourcesFromCatalog("2AGL")
        assert 175==len(added)
        assert 175==len(sl.sources)

        with pytest.raises(FileNotFoundError):
            sl.loadSourcesFromCatalog("paperino")


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    def test_load_catalog_from_catalog_filtering_on_distances(self, configObject, logger):
        sl = SourcesLibrary(configObject, logger)

        added = sl.loadSourcesFromCatalog("2AGL", rangeDist=(70, 80))

        assert 13 == len(added)
        assert 13 == len(sl.sources)

        sl.sources = []
        added = sl.loadSourcesFromCatalog("2AGL", rangeDist=(0, 10))
        assert 1 == len(added)
        assert 1 == len(sl.sources)

        sl.sources = []
        added = sl.loadSourcesFromCatalog("2AGL", rangeDist=(0, 50))
        assert 30 == len(added)
        assert 30 == len(sl.sources)


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.xml")
    def test_load_sources_from_xml_file(self, configObject, logger, testdata):
        sl = SourcesLibrary(configObject, logger)

        added = sl.loadSourcesFromFile(testdata)

        assert 2== len(added)
        assert 2== len(sl.sources)

        sources = sl.selectSources('name == "2AGLJ2021+4029"')
        assert 1 == len(sources)
        source = sources.pop()
        assert 119.3e-08== source.spectrum.getVal("flux")
        assert 1.75== source.spectrum.getVal("index")
        assert 78.2375== source.spatialModel.getVal("pos")[0]
        assert source.spatialModel.getVal("dist") > 0

        sources = sl.selectSources('name == "2AGLJ2021+3654"')
        assert 1== len(sources)
        source = sources.pop()
        assert 70.89e-08== source.spectrum.getVal("flux")
        assert 1.38== source.spectrum.getVal("index")
        assert 75.2562== source.spatialModel.getVal("pos")[0]
        assert source.spatialModel.getVal("dist") > 0


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.txt")
    def test_load_sources_from_txt_file(self, configObject, logger, testdata):
        sl = SourcesLibrary(configObject, logger)

        added = sl.loadSourcesFromFile(testdata)

        assert 10== len(added)
        assert 10== len(sl.sources)

        sources = sl.selectSources('name == "2AGLJ1801-2334"')
        assert 1== len(sources)
        source = sources.pop()

        assert 3.579e-07== source.spectrum.getVal("flux")
        assert 3.37991== source.spectrum.getVal("index")
        assert 6.16978== source.spatialModel.getVal("pos")[0]

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

            assert fs[i] == TestSourcesLibrary.get_free_params(sl.sources[i])


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.txt")
    def test_fixflag(self, configObject, logger, testdata):
        sl = SourcesLibrary(configObject, logger)

        added = sl.loadSourcesFromFile(testdata)
        results_fixflag = []

        for source in sl.sources:
            fixflag = SourcesLibrary._computeFixFlag(source, source.spectrum.getType())
            results_fixflag.append(fixflag)

        assert results_fixflag == ['0','1','2','3','4','5','7','28','30','32']

        

    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/testcase_2AGLJ0835-4514.source")
    def test_source_file_parsing(self, configObject, logger, testdata):
        sl = SourcesLibrary(configObject, logger)

        sourceFile = testdata

        res = sl.parseSourceFile(sourceFile)

        assert True== bool(res)

        assert True== isinstance(res.multiFlux["value"], float)
        assert 9.07364e-06== res.multiFlux["value"]
        assert True== isinstance(res.multiSqrtTS["value"], float)
        assert 2.17268== res.multiSqrtTS["value"]
        assert None== res.multiDist["value"]


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    def test_load_source_from_catalog_without_scaling(self, configObject, logger):
        sl = SourcesLibrary(configObject, logger)

        sources = sl.loadSourcesFromCatalog(catalogName="2AGL")

        assert 175== len(sources)

        assert 7.45398e-08== sources[0].spectrum.getVal("flux")


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    def test_load_source_from_catalog_with_scaling(self, configObject, logger):
        sl = SourcesLibrary(configObject, logger)

        configObject.setOptions(emin=10, emax=1000)

        sources = sl.loadSourcesFromCatalog(catalogName="2AGL")

        assert 175== len(sources)

        assert 6.940938928095228e-07== sources[0].spectrum.getVal("flux")


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.xml")
    @pytest.mark.testdatafile2("core/test_data/testcase_2AGLJ2021+3654.source")
    def test_select_sources_with_selection_string(self, configObject, logger, testdata, testdata2):
        sl = SourcesLibrary(configObject, logger)

        sl.loadSourcesFromFile(testdata)
        assert 2== len(sl.sources)
        
        sources = sl.selectSources('name == "2AGLJ2021+3654" AND flux > 0')
        assert 1== len(sources)

        sourceFile = testdata2

        mleAnalysisResults = sl.parseSourceFile(sourceFile)

        sl.updateSourceWithMLEResults(mleAnalysisResults)

        sources = sl.selectSources('name == "2AGLJ2021+3654" AND flux > 0')
        assert 1 ==len(sources)

        sources = sl.selectSources('multisqrtts == 10')
        assert 1 == len(sources)

        sources = sl.selectSources('sqrtts == 10')
        assert 1 == len(sources)
        

    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.xml")
    @pytest.mark.testdatafile2("core/test_data/testcase_2AGLJ2021+3654.source")
    def test_select_sources_with_selection_lambda(self, configObject, logger, testdata, testdata2):
        sl = SourcesLibrary(configObject, logger)

        sl.loadSourcesFromFile(testdata)

        sources = sl.selectSources( lambda name : name == "2AGLJ2021+3654" )
        assert 1 == len(sources)

        sourceFile = testdata2

        mleAnalysisResults = sl.parseSourceFile(sourceFile)

        sl.updateSourceWithMLEResults(mleAnalysisResults)

        sources = sl.selectSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0)
        assert 1== len(sources)



    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.xml")
    @pytest.mark.testdatafile2("core/test_data/testcase_2AGLJ2021+3654.source")
    def test_free_sources_with_selection_string(self, configObject, logger, testdata, testdata2):
        sl = SourcesLibrary(configObject, logger)

        sl.loadSourcesFromFile(testdata)
        sourceFile = testdata2
        mleAnalysisResults = sl.parseSourceFile(sourceFile)
        sl.updateSourceWithMLEResults(mleAnalysisResults)

        sources = sl.freeSources('name == "2AGLJ2021+3654" AND flux > 0', "flux", False)

        assert 1== len(sources)
        assert "flux" not in sources[0].getFreeParams()

        sources = sl.freeSources('name == "2AGLJ2021+3654" AND flux > 0', "flux", True)
        assert "flux" in sources[0].getFreeParams()

        sources = sl.freeSources('name == "2AGLJ2021+3654" AND flux > 0', "index", True)
        assert "index" in sources[0].getFreeParams()

        sources = sl.freeSources('name == "2AGLJ2021+3654" AND flux > 0', "index", False)
        assert "index" not in sources[0].getFreeParams()



    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.xml")
    @pytest.mark.testdatafile2("core/test_data/testcase_2AGLJ2021+3654.source")
    def test_free_sources_with_selection_lambda(self, configObject, logger, testdata, testdata2):
        sl = SourcesLibrary(configObject, logger)

        sl.loadSourcesFromFile(testdata)
        sourceFile = testdata2
        mleAnalysisResults = sl.parseSourceFile(sourceFile)
        sl.updateSourceWithMLEResults(mleAnalysisResults)

        sources = sl.freeSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0, "flux", False)
        assert 1, len(sources)
        assert "flux" not in sources[0].getFreeParams()

        sources = sl.freeSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0, "flux", True)
        assert "flux" in sources[0].getFreeParams()

        sources = sl.freeSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0, "index", True)
        assert "index" in sources[0].getFreeParams()

        sources = sl.freeSources(lambda name, flux : name == "2AGLJ2021+3654" and flux > 0, "index", False)
        assert "index" not in sources[0].getFreeParams()


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.xml")
    def test_write_to_file_xml(self, config, configObject, logger, testdata):
        sl = SourcesLibrary(configObject, logger)

        configObject = AgilepyConfig()

        configObject.loadBaseConfigurations(config)

        sl.loadSourcesFromFile(testdata)

        outfileName = "write_to_file_testcase"

        outputFile = Path(sl.writeToFile(outfileName, fileformat="xml"))

        assert True== outputFile.exists()

        sourcesxml = parse(outputFile).getroot()

        assert 2== len(sourcesxml)


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sourcesconf_for_write_to_file_txt.txt")
    def test_write_to_file_txt(self, config, configObject, logger, testdata):
        sl = SourcesLibrary(configObject, logger)

        configObject = AgilepyConfig()

        configObject.loadBaseConfigurations(config)

        sourcesFile = testdata

        sl.loadSourcesFromFile(sourcesFile)

        outfileName = "write_to_file_testcase"

        outputFile = Path(sl.writeToFile(outfileName, fileformat="txt"))

        assert True== outputFile.exists()

        with open(outputFile) as of:
            lines = of.readlines()

        assert "1.57017e-07 80.3286 1.12047 2.16619 0 2 _2AGLJ2032+4135 0 0 0 0 0.5 5.0 20 10000 0 100"== lines[0].strip()
        assert "1.69737e-07 79.9247 0.661449 1.99734 0 2 CYGX3 0 0 0 0 0.5 5.0 20 10000 0 100"== lines[1].strip()
        assert "1.19303e-06 78.2375 2.12298 1.75823 3 2 _2AGLJ2021+4029 0 1 3307.63 0 0.5 5.0 20.0 10000.0  0 100"== lines[2].strip()


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.xml")
    def test_add_source(self, config, configObject, logger, testdata):
        sl = SourcesLibrary(configObject, logger)

        configObject = AgilepyConfig()

        configObject.loadBaseConfigurations(config)

        sl.loadSourcesFromFile(testdata)

        newSourceDict = {
            "a" : 10
        }
        with pytest.raises(SourceParamNotFoundError):
            sl.addSource("newsource", newSourceDict)


        newSourceDict = {
            "glon" : 250,
            "glat": 30,
            "spectrumType" : "LogPaperone"
        }
        with pytest.raises(SpectrumTypeNotFoundError):
            sl.addSource("newsource", newSourceDict)

        newSourceDict = {
            "glon" : 250,
            "glat": 30,
            "spectrumType" : "LogParabola"
        }
        with pytest.raises(SourceParamNotFoundError):
            sl.addSource("", newSourceDict)
            sl.addSource(None, newSourceDict)
            sl.addSource("newsource", newSourceDict)

        newSourceDict = {
            "glon" : 250,
            "glat": 30,
            "spectrumType" : "LogParabola",
            "flux": 40,
            "index": 2,
            "pivotEnergy": 4,
            "curvature": 5
        }
        newSourceObj = sl.addSource("newsource", newSourceDict)

        assert True, isinstance(newSourceObj, PointSource)

        newSource = sl.selectSources('name == "newsource"').pop()

        assert 40== newSource.spectrum.getVal("flux")
        assert 5== newSource.spectrum.getVal("curvature")
        assert "newsource"== newSource.name
        assert 35.2462913047547== newSource.spatialModel.getVal("dist")


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    def test_convert_catalog_to_xml(self, configObject, logger):
        sl = SourcesLibrary(configObject, logger)

        catalogFile = "$AGILE/catalogs/2AGL.multi"

        outfile = sl.convertCatalogToXml(catalogFile)

        sourcesxml = parse(outfile).getroot()

        assert 175== len(sourcesxml)

        added = sl.loadSourcesFromFile(outfile)

        assert 175== len(added)

        assert 175== len(sl.sources)


    @pytest.mark.testlogsdir("core/test_logs/test_sources_library")
    @pytest.mark.testconfig("core/conf/agilepyconf.yaml")
    @pytest.mark.testdatafile("core/test_data/sources_2.xml")    
    def test_backup_restore(self, config, configObject, logger, testdata):
        sl = SourcesLibrary(configObject, logger)

        configObject = AgilepyConfig()

        configObject.loadBaseConfigurations(config)

        sl.loadSourcesFromFile(testdata)

        """
        for s in sl.getSources():
            print(s)
        """
        
        assert 2== len(sl.sources)

        sl.backupSL()

        sl.deleteSources('name=="2AGLJ2021+4029"')

        assert 1== len(sl.sources)

        sl.deleteSources('name=="2AGLJ2021+3654"')

        assert 0== len(sl.sources)

        sl.restoreSL()

        assert 2== len(sl.sources)
 