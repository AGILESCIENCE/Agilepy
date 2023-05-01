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
from time import sleep
from pathlib import Path
from datetime import datetime

from agilepy.utils.Utils import Utils
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.utils.PlottingUtils import PlottingUtils
from agilepy.config.AgilepyConfig import AgilepyConfig

class AgilepyUtilsUT(unittest.TestCase):

    def setUp(self):
        self.currentDirPath = Path(__file__).parent.absolute()
        self.agilepyconfPath = os.path.join(self.currentDirPath,"conf/agilepyconf.yaml")

        self.config = AgilepyConfig()
        self.config.loadBaseConfigurations(self.agilepyconfPath)

        self.agilepyLogger = AgilepyLogger()

        self.agilepyLogger.initialize(self.config.getConf("output","outdir"), self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))

        self.datadir = os.path.join(self.currentDirPath,"data")

        self.outDir = Path(self.config.getOptionValue("outdir"))

        if self.outDir.exists() and self.outDir.is_dir():
            self.agilepyLogger.reset()
            shutil.rmtree(self.outDir)

        self.tmpDir = Path("./tmp")
        self.tmpDir.mkdir(exist_ok=True)

    def tearDown(self):
        self.agilepyLogger.reset()
        if self.tmpDir.exists() and self.tmpDir.is_dir():
            shutil.rmtree(self.tmpDir)

    def test_display_sky_map(self):

        pu = PlottingUtils(self.config, self.agilepyLogger)

        smooth = 4
        fileFormat = ".png"
        title = "testcase"
        cmap = "CMRmap"
        regFiles = [Utils._expandEnvVar("$AGILE/catalogs/2AGL_2.reg"), Utils._expandEnvVar("$AGILE/catalogs/2AGL_2.reg")]
        regFileColors = ["yellow", "blue"]


        file = pu.displaySkyMap(
                    self.datadir+"/testcase_EMIN00100_EMAX00300_01.cts.gz", \
                    smooth = smooth,
                    fileFormat = fileFormat,
                    title = title,
                    cmap = cmap,
                    regFiles = regFiles,
                    regFileColors=regFileColors,
                    catalogRegions = "2AGL",
                    catalogRegionsColor = "red",
                    saveImage=True,
                    normType="linear")

        assert True == os.path.isfile(file)

    def test_display_sky_map_single_mode_3_imgs(self):

        pu = PlottingUtils(self.config, self.agilepyLogger)

        smooth = 4
        fileFormat = ".png"
        title = "testcase"
        cmap = "CMRmap"
        regFiles = [Utils._expandEnvVar(
            "$AGILE/catalogs/2AGL_2.reg"), Utils._expandEnvVar("$AGILE/catalogs/2AGL_2.reg")]
        regFileColors = ["yellow", "blue"]
        img = self.datadir+"/testcase_EMIN00100_EMAX00300_01.cts.gz"

        file = pu.displaySkyMapsSingleMode(
                    [img, img, img], \
                    smooth = smooth,
                    fileFormat = fileFormat,
                    titles = [title+"_1", title+"_2", title+"_3"],
                    cmap = cmap,
                    regFiles = regFiles,
                    regFileColors=regFileColors,
                    catalogRegions = "2AGL",
                    catalogRegionsColor = "red",
                    saveImage=True,
                    normType="linear")

        assert True == os.path.isfile(file)

    def test_display_sky_map_single_mode_2_imgs(self):

        pu = PlottingUtils(self.config, self.agilepyLogger)

        smooth = 4
        fileFormat = ".png"
        title = "testcase"
        cmap = "CMRmap"
        regFiles = [Utils._expandEnvVar(
            "$AGILE/catalogs/2AGL_2.reg"), Utils._expandEnvVar("$AGILE/catalogs/2AGL_2.reg")]
        regFileColors = ["yellow", "blue"]
        img = self.datadir+"/testcase_EMIN00100_EMAX00300_01.cts.gz"

        file = pu.displaySkyMapsSingleMode(
                    [img, img], \
                    smooth = smooth,
                    fileFormat = fileFormat,
                    titles = [title+"_1", title+"_2", title+"_3"],
                    cmap = cmap,
                    regFiles = regFiles,
                    regFileColors=regFileColors,
                    catalogRegions = "2AGL",
                    catalogRegionsColor = "red",
                    saveImage=True,
                    normType="linear")

        assert True == os.path.isfile(file)



    def test_plot_data_availability(self):

        outputDir = self.currentDirPath.joinpath("output", "test_plot_data_availability")
        outputDir.mkdir(parents=True, exist_ok=True)
        os.environ["TEST_LOGS_DIR"] = str(outputDir)
        
        config = AgilepyConfig()
        config.loadBaseConfigurations(self.currentDirPath.joinpath("conf", "test_plot_data_availability.yaml"))

        pu = PlottingUtils(config, self.agilepyLogger)

        dataDir = Path(self.datadir).joinpath("test_plot_data_availability")

        pu.plotDataAvailability(dataDir.joinpath("EVT.qfile"), dataDir.joinpath("EVT.index"), saveImage=True)

        #pu.plotDataAvailability(dataDir.joinpath("LOG.qfile"), dataDir.joinpath("LOG.index"), saveImage=True)




    def test_initialize_logger_verboselvl_2(self):
        sleep(1.0)
        self.agilepyLogger.reset()

        self.config.loadBaseConfigurations(os.path.join(self.currentDirPath,"conf/agilepyconf_verbose_2.yaml"))
        
        logfilePath = self.agilepyLogger.initialize(self.config.getOptionValue("outdir"), self.config.getOptionValue("logfilenameprefix"), self.config.getOptionValue("verboselvl"))

        assert True == logfilePath.is_file()

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            assert 1 == linesNumber

        self.agilepyLogger.debug(self, "%s %s", "Debug", "message")
        self.agilepyLogger.info(self, "%s %s", "Info", "message")
        self.agilepyLogger.warning(self, "%s %s", "Warning", "message")
        self.agilepyLogger.critical(self, "%s %s", "Critical", "message")

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            assert 5 == linesNumber

    def test_initialize_logger_verboselvl_1(self):
        sleep(1.0)
        self.agilepyLogger.reset()

        self.config.loadBaseConfigurations(os.path.join(self.currentDirPath,"conf/agilepyconf_verbose_1.yaml"))

        logfilePath = self.agilepyLogger.initialize(self.config.getOptionValue("outdir"), self.config.getOptionValue("logfilenameprefix"), self.config.getOptionValue("verboselvl"))

        assert True == logfilePath.is_file()

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            assert 1 == linesNumber

        self.agilepyLogger.debug(self, "%s %s", "Debug", "message")
        self.agilepyLogger.info(self, "%s %s", "Info", "message")
        self.agilepyLogger.warning(self, "%s %s", "Warning", "message")
        self.agilepyLogger.critical(self, "%s %s", "Critical", "message")

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            assert 5 == linesNumber

    def test_initialize_logger_verboselvl_0(self):
        sleep(1.0)
        self.agilepyLogger.reset()

        self.config.loadBaseConfigurations(os.path.join(self.currentDirPath,"conf/agilepyconf_verbose_0.yaml"))

        logfilePath = self.agilepyLogger.initialize(self.config.getOptionValue("outdir"), self.config.getOptionValue("logfilenameprefix"), self.config.getOptionValue("verboselvl"))

        assert True == logfilePath.is_file()

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            assert 1 == linesNumber

        self.agilepyLogger.debug(self, "%s %s", "Debug", "message")
        self.agilepyLogger.info(self, "%s %s", "Info", "message")
        self.agilepyLogger.warning(self, "%s %s", "Warning", "message")
        self.agilepyLogger.critical(self, "%s %s", "Critical", "message")

        with open(logfilePath, "r") as f:
            linesNumber = len(f.readlines())
            assert 5 == linesNumber

    def test_filterAP(self):
    
        print(self.datadir+"/E1q1_604800s_emin100_emax10000_r2.ap")
        print(self.currentDirPath)
        product = AstroUtils.AP_filter(
            self.datadir+"/E1q1_604800s_emin100_emax10000_r2.ap", 1, 174142800, 447490800, self.currentDirPath)
        with open(product, "r") as f:
            linesNumber = len(f.readlines())
            assert 4 == linesNumber
        
        os.remove(os.path.join(self.currentDirPath, "result.txt"))
        os.remove(os.path.join(self.currentDirPath, product))

    """
    Time conversions
        # https://tools.ssdc.asi.it/conversionTools
        # https://heasarc.gsfc.nasa.gov/cgi-bin/Tools/xTime/xTime.pl?time_in_i=&time_in_c=&time_in_d=&time_in_j=&time_in_m=58871.45616898&time_in_sf=&time_in_wf=&time_in_sl=&time_in_sni=&time_in_snu=&time_in_s=&time_in_h=&time_in_sz=&time_in_ss=&time_in_sn=&timesys_in=u&timesys_out=u&apply_clock_offset=yes
    """
    def test_astro_utils_time_mjd_to_agile_seconds(self):
        sec_tolerance = 0.001
        tt = AstroUtils.time_mjd_to_agile_seconds(58871.45616898) # 506861812.99987227
        assert abs(506861813-tt) <= sec_tolerance

    def test_astro_utils_time_agile_seconds_to_mjd(self):
        sec_tolerance = 0.0000001
        mjd = AstroUtils.time_agile_seconds_to_mjd(507391426.9447)
        assert abs(58877.58595999 - mjd) <= sec_tolerance

    def test_astro_utils_time_utc_to_jd(self):

        tol = 0.00000001

        dt = "2020-01-23T10:56:53.000"

        jd = AstroUtils.time_fits_to_jd(dt)

        assert abs(2458871.95616898 - jd) <= tol

    def test_astro_utils_time_utc_to_mjd(self):

        tol = 0.00000001

        dt = "2020-01-23T10:56:53.000"

        mjd = AstroUtils.time_fits_to_mjd(dt)

        assert abs(58871.45616898 - mjd) <= tol

    def test_astro_utils_time_utc_to_tt(self):

        tol = 0.0001

        agileseconds = AstroUtils.time_fits_to_agile_seconds("2020-01-23T10:56:53.000")

        assert abs(506861813 - agileseconds) <= tol

    def test_astro_utils_time_agile_seconds_to_jd(self):
        jd = AstroUtils.time_agile_seconds_to_jd(449582332)
        assert jd == pytest.approx(2458208.99921296, 0.00001)


    def test_astro_utils_time_agile_seconds_to_utc(self):

        sec_tol = 1
        """
        utc = AstroUtils.time_tt_to_utc(506861813)
        dt = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S.%f')

        assert dt.year == 2020
        assert dt.month == 1
        assert dt.day == 23
        assert dt.hour == 10
        assert dt.minute == 56
        assert abs(53 - dt.second) <= sec_tol
        """

        # This date would result in "0 days"
        fitstime = AstroUtils.time_agile_seconds_to_fits(449582332)
        dt = datetime.strptime(fitstime, '%Y-%m-%dT%H:%M:%S.%f')

        assert dt.year == 2018
        assert dt.month == 3
        assert dt.day == 31
        assert dt.hour == 11
        assert dt.minute == 58
        assert abs(52 - dt.second) <= sec_tol


    def test_astro_utils_time_mjd_to_fits(self):

        sec_tol = 1

        fitstime = AstroUtils.time_mjd_to_fits(58871.45616898)

        dt = datetime.strptime(fitstime, '%Y-%m-%dT%H:%M:%S.%f')

        assert dt.year == 2020
        assert dt.month == 1
        assert dt.day == 23
        assert dt.hour == 10
        assert dt.minute == 56
        assert abs(53 - dt.second) <= sec_tol

    def test_astro_utils_time_fits_to_mjd_2(self):

        sec_tol = 0.00000001

        mjd = AstroUtils.time_fits_to_mjd("2020-01-23T10:56:53.000")

        assert abs(58871.45616898 - mjd) <= sec_tol

    def test_get_first_and_last_line_in_file(self):

        line1 = '/ASDC_PROC2/FM3.119_2/EVT/agql2004151750_2004151850.EVT__FM.gz 514057762.000000 514061362.000000 EVT\n'
        line2 = '/ASDC_PROC2/FM3.119_2/EVT/agql2004152249_2004160008.EVT__FM.gz 514075704.000000 514080437.000000 EVT\n'
        line3 = '/ASDC_PROC2/FM3.119_2/EVT/agql2004160008_2004160045.EVT__FM.gz 514080437.000000 514082644.000000 EVT\n'

        # I test: 1 line
        test_file = self.tmpDir.joinpath("test_file1.txt")
        with open(test_file, "w") as f:
            f.write(line1)
        (first, last) = Utils._getFirstAndLastLineInFile(test_file)
        assert first == line1
        assert last == line1

        # II test: 2 lines
        test_file = self.tmpDir.joinpath("test_file2.txt")
        with open(test_file, "w") as f:
            f.write(line1)
            f.write(line2)
        (first, last) = Utils._getFirstAndLastLineInFile(test_file)
        assert first == line1
        assert last == line2

        # III test: 3 lines
        test_file = self.tmpDir.joinpath("test_file3.txt")
        with open(test_file, "w") as f:
            f.write(line1)
            f.write(line2)
            f.write(line3)
        (first, last) = Utils._getFirstAndLastLineInFile(test_file)
        assert first == line1
        assert last == line3

    """
    def test_sort_index_file(self):
        evtfileIndex = Path(self.datadir).joinpath("indexfile_not_ordered.test")
        copy = evtfileIndex.with_suffix(".2")
        shutil.copy(evtfileIndex, copy)
        Utils.sortIndexFile(copy)
        with open(copy, 'r') as fh:
            lines = fh.readlines()
        assert lines[0] == "/pippoz/a.gz 10.100000 371995132.000000 EVT"
        assert lines[1] == "/pippoz/b.gz 20.200000 371995132.000000 EVT"
        assert lines[2] == "/pippoz/c.gz 30.300000 371995132.000000 EVT"
        assert lines[3] == "/pippoz/d.gz 40.400000 371995132.000000 EVT"
        assert lines[4] == "/pippoz/e.gz 50.500000 371995132.000000 EVT"
    """
        

if __name__ == '__main__':
    unittest.main()
