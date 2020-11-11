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
from agilepy.api.AGAnalysisWavelet import AGAnalysisWavelet

class AGAnalysisWaveletUT(unittest.TestCase):

    def testGetConfiguration(self):

        confFile = "./agilepy_conf.yaml"

        AGAnalysisWavelet.getConfiguration(
        confFilePath=confFile,
        userName="Anto",
        outputDir="$HOME/test_wavelet",
        verboselvl=2,
        ctsmap="/data01/homes/addis/Agilepy/agilepy/testing/unittesting/api/data/analysis_product_EMIN00100_EMAX10000_01.cts.gz",
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

        self.assertEqual(True, os.path.isfile(confFile))

        os.remove(confFile)

    def testWaveletInstance(self):

        confFile = "./agilepy_conf.yaml"

        AGAnalysisWavelet.getConfiguration(
        confFilePath=confFile,
        userName="Anto",
        outputDir="$HOME/test_wavelet",
        verboselvl=2,
        ctsmap="/data01/homes/addis/Agilepy/agilepy/testing/unittesting/api/data/analysis_product_EMIN00100_EMAX10000_01.cts.gz",
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

        self.assertEqual(True, os.path.isfile(confFile))

        self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet")))

        os.remove(confFile)
        #os.remove(os.path.expandvars("$HOME/test_wavelet"))

    def testWaveletAnalysis(self):

        confFile = "./agilepy_conf.yaml"

        AGAnalysisWavelet.getConfiguration(
        confFilePath=confFile,
        userName="Anto",
        outputDir="$HOME/test_wavelet",
        verboselvl=2,
        ctsmap="/data01/homes/addis/Agilepy/agilepy/testing/unittesting/api/data/analysis_product_EMIN00100_EMAX10000_01.cts.gz",
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

        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/cwt2")))
        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/met")))
        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/ccl")))
        
        self.assertEqual(True,os.path.isfile(os.path.expandvars(f1)))
        self.assertEqual(True,os.path.isfile(os.path.expandvars(f2)))
        self.assertEqual(True,os.path.isfile(os.path.expandvars(f3)))


        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/cwt2")))
        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/met")))
        # self.assertEqual(True,os.path.isdir(os.path.expandvars("$HOME/test_wavelet/ccl")))
        
        # self.assertEqual(True,os.path.isfile(os.path.expandvars("$HOME/test_wavelet/cwt2/wavelet_product_CWT2.wtf")))
        # self.assertEqual(True,os.path.isfile(os.path.expandvars("$HOME/test_wavelet/met/wavelet_product_MET.met")))
        # self.assertEqual(True,os.path.isfile(os.path.expandvars("$HOME/test_wavelet/ccl/wavelet_product_CCL.list")))




        os.remove(confFile)
        #os.remove(os.path.expandvars("$HOME/test_wavelet"))



if __name__ == '__main__':
    unittest.main()
