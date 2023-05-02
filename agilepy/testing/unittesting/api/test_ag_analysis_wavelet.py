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

from agilepy.api.AGAnalysisWavelet import AGAnalysisWavelet

class TestAGAnalysisWavelet:

    @pytest.mark.testlogsdir("api/test_logs/test_get_configuration")
    @pytest.mark.testdatafiles(["api/data/analysis_product_EMIN00100_EMAX10000_01.cts.gz"])  
    def test_get_configuration(self, logger, testdatafiles):

        confFile = "/tmp/agilepy_conf.yaml"

        AGAnalysisWavelet.getConfiguration(
            confFilePath=confFile,
            userName="Anto",
            outputDir="$HOME/test_wavelet",
            verboselvl=2,
            ctsmap=testdatafiles.pop(),
            scaletype="dyadic",
            scalemin=2,
            scalemax=1024,
            scalenum=50,
            methistsize=1000,
            cclsizemin=-1,
            cclsizemax=-1,
            cclradmin=-1,
            cclradmax=-1,
            cclscalemin=-1,
            cclscalemax=-1
        )

        assert Path(confFile).is_file()

 
    @pytest.mark.testlogsdir("api/test_logs/test_wavelet_analysis")
    @pytest.mark.testdatafiles(["api/data/analysis_product_EMIN00100_EMAX10000_01.cts.gz"])    
    def test_wavelet_analysis(self, logger, testdatafiles):
        
        confFile = "/tmp/agilepy_conf.yaml"

        AGAnalysisWavelet.getConfiguration(
            confFilePath=confFile,
            userName="AgilepyTest",
            outputDir="/tmp/test_wavelet",
            verboselvl=2,
            ctsmap=testdatafiles.pop(),
            scaletype="dyadic",
            scalemin=2,
            scalemax=1024,
            scalenum=50,
            methistsize=1000,
            cclsizemin=-1,
            cclsizemax=-1,
            cclradmin=-1,
            cclradmax=-1,
            cclscalemin=-1,
            cclscalemax=-1
        )

        ag = AGAnalysisWavelet(confFile)
        f1, f2, f3 = ag.waveletAnalysis()

        assert Path(f1).is_file()
        assert Path(f2).is_file()
        assert Path(f3).is_file()


        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/cwt2")))
        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/met")))
        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/ccl")))
        
        # self.assertEqual(True,os.path.isfile(os.path.expandvars("$HOME/test_wavelet/cwt2/wavelet_product_CWT2.wtf")))
        # self.assertEqual(True,os.path.isfile(os.path.expandvars("$HOME/test_wavelet/met/wavelet_product_MET.met")))
        # self.assertEqual(True,os.path.isfile(os.path.expandvars("$HOME/test_wavelet/ccl/wavelet_product_CCL.list")))



 