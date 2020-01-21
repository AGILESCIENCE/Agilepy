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

from agilepy.utils.Parameters import Parameters
from agilepy.utils.ProcessWrapper import ProcessWrapper

class CtsMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)

    def getRequiredOptions(self):
        return ["evtfile", "outdir", "filenameprefix", "emin", "emax", "energybins", "glat", "glon", "tmin", "tmax"]

    def configure(self, confDict):

        self.outputDir = os.path.join(confDict.getOptionValue("outdir"), "maps")
        outputName = confDict.getOptionValue("filenameprefix")+".cts.gz"

        self.outfilePath = os.path.join(self.outputDir, outputName)

        self.products = [self.outfilePath]

        self.args = [ self.outfilePath,  \
                      confDict.getOptionValue("evtfile"), #indexfiler\
                      confDict.getOptionValue("timelist"), \
                      confDict.getOptionValue("mapsize"), \
                      confDict.getOptionValue("binsize"), \
                      confDict.getOptionValue("glon"), \
                      confDict.getOptionValue("glat"), \
                      confDict.getOptionValue("lonpole"), \
                      confDict.getOptionValue("albedorad"), \
                      confDict.getOptionValue("phasecode"), \
                      confDict.getOptionValue("filtercode"), \
                      confDict.getOptionValue("proj"), \
                      confDict.getOptionValue("tmin"), \
                      confDict.getOptionValue("tmax"), \
                      confDict.getOptionValue("emin"), \
                      confDict.getOptionValue("emax"), \
                      confDict.getOptionValue("fovradmin"), \
                      confDict.getOptionValue("fovradmax"), \
                    ]





class ExpMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)


    def getRequiredOptions(self):
        return ["logfile", "outdir", "filenameprefix", "emin", "emax", "glat", "glon", "tmin", "tmax"]

    def configure(self, confDict):

        self.outputDir = os.path.join(confDict.getOptionValue("outdir"), "maps")
        outputName = confDict.getOptionValue("filenameprefix")+".exp.gz"

        edpmatrix = "None"
        if confDict.getOptionValue("useEDPmatrixforEXP"):
            edpmatrix = Parameters.edpmatrix

        self.outfilePath = os.path.join(self.outputDir, outputName)

        self.products = [self.outfilePath]

        self.args = [ self.outfilePath,  \
                      confDict.getOptionValue("logfile"), #indexfiler\
                      Parameters.sarmatrix, \
                      edpmatrix, \
                      confDict.getOptionValue("maplistgen"), \
                      confDict.getOptionValue("timelist"), \
                      confDict.getOptionValue("mapsize"), \
                      confDict.getOptionValue("binsize"), \
                      confDict.getOptionValue("glon"), \
                      confDict.getOptionValue("glat"), \
                      confDict.getOptionValue("lonpole"), \
                      confDict.getOptionValue("albedorad"), \
                      0.5, \
                      360, \
                      5.0, \
                      confDict.getOptionValue("phasecode"), \
                      confDict.getOptionValue("proj"), \
                      confDict.getOptionValue("expstep"), \
                      confDict.getOptionValue("timestep"), \
                      confDict.getOptionValue("spectralindex"), \
                      confDict.getOptionValue("tmin"), \
                      confDict.getOptionValue("tmax"), \
                      confDict.getOptionValue("emin"), \
                      confDict.getOptionValue("emax"), \
                      confDict.getOptionValue("fovradmin"), \
                      confDict.getOptionValue("fovradmax"), \
                    ]




class GasMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix", "expmap"]

    def configure(self, confDict):

        self.outputDir = os.path.join(confDict.getOptionValue("outdir"), "maps")
        outputName = confDict.getOptionValue("filenameprefix")+".gas.gz"

        self.outfilePath = os.path.join(self.outputDir, outputName)

        self.products = [self.outfilePath]

        self.args = [ expMapGenerator.outfilePath, \
                      self.outfilePath,  \
                      confDict.getOptionValue("skymapL"), \
                      confDict.getOptionValue("skymaH"), \
                    ]




class IntMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix", "expmap", "ctsmap"]

    def configure(self, confDict):

        self.outputDir = os.path.join(confDict.getOptionValue("outdir"), "maps")
        outputName = confDict.getOptionValue("filenameprefix")+".int.gz"
        self.outfilePath = os.path.join(self.outputDir, outputName)

        self.products = [self.outfilePath]

        self.args = [ expMapGenerator.outfilePath, \
                      self.outfilePath,  \
                      ctsMapGenerator.outfilePath, \
                    ]






class Multi(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix"]

    def configure(self, confDict):

        self.outputDir = os.path.join(confDict.getOptionValue("outdir"), "mle")
        outputName = confDict.getOptionValue("filenameprefix")+(str(self.callCounter).zfill(4))
        self.outfilePath = os.path.join(self.outputDir, outputName)

        self.products = []
        for sourceName in confDict.getOptionValue("multisources"):
            prodName = os.path.join(self.outputDir, outputName+"_"+sourceName+".source")
            self.products.append(prodName)

        expratioevaluation = 0
        if confDict.getOptionValue("expratioevaluation"):
            expratioevaluation = 1

        self.args = [
            confDict.getOptionValue("maplist"), \
            Parameters.matrixconf, \
            confDict.getOptionValue("ranal"), \
            confDict.getOptionValue("galmode"), \
            confDict.getOptionValue("isomode"), \
            confDict.getOptionValue("sourcelist"), \
            self.outfilePath, \
            confDict.getOptionValue("ulcl"), \
            confDict.getOptionValue("loccl"), \
            confDict.getOptionValue("galmode2"), \
            confDict.getOptionValue("galmode2fit"), \
            confDict.getOptionValue("isomode2"), \
            confDict.getOptionValue("isomode2fit"), \
            confDict.getOptionValue("edpcorrection"), \
            confDict.getOptionValue("fluxcorrection"), \
            confDict.getOptionValue("minimizertype"), \
            confDict.getOptionValue("minimizeralg"), \
            confDict.getOptionValue("minimizerdefstrategy"), \
            confDict.getOptionValue("mindefaulttolerance"), \
            confDict.getOptionValue("integratortype"), \
            expratioevaluation, \
            confDict.getOptionValue("expratio_minthr"), \
            confDict.getOptionValue("expratio_maxthr"), \
            confDict.getOptionValue("expratio_size"), \
            confDict.getOptionValue("contourpoints"),
        ]






ctsMapGenerator = CtsMapGenerator("AG_ctsmapgen")
expMapGenerator = ExpMapGenerator("AG_expmapgen")
gasMapGenerator = GasMapGenerator("AG_gasmapgen")
intMapGenerator = IntMapGenerator("AG_intmapgen")
multi = Multi("AG_multi")
