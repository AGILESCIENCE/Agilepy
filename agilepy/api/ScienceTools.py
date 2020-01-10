"""
 DESCRIPTION
       Agilepy software

 NOTICE
       Any information contained in this software
       is property of the AGILE TEAM and is strictly
       private and confidential.
       Copyright (C) 2005-2020 AGILE Team.
           Addis Antonio <antonio.addis@inaf.it>
           Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
           Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
           Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
       All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from agilepy.utils.ProcessWrapper import *


class CtsMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)

    def getRequiredOptions(self):
        return ["evtfile", "outdir", "mapnameprefix", "emin", "emax", "energybins", "glat", "glon", "tmin", "tmax"]

    def setArguments(self, confDict):

        if not self.allRequiredOptionsSet(confDict, self.getRequiredOptions()):
            self.logger.critical(self,"Some options have not been set.")
            exit(1)

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("mapnameprefix")+".cts.gz"

        self.outfilePath = os.path.join(outDir, outputName)

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


    def parseOutput(self):
        pass



class ExpMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)


    def getRequiredOptions(self):
        return ["evtfile", "outdir", "mapnameprefix", "emin", "emax", "glat", "glon", "tmin", "tmax"]

    def setArguments(self, confDict):

        if not self.allRequiredOptionsSet(confDict, self.getRequiredOptions()):
            self.logger.critical(self,"Some options have not been set.")
            exit(1)

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("mapnameprefix")+".exp.gz"

        edpmatrix = "None"
        if confDict.getOptionValue("useEDPmatrixforEXP"):
            edpmatrix = Parameters.edpmatrix

        self.outfilePath = os.path.join(outDir, outputName)

        self.args = [ self.outfilePath,  \
                      confDict.getOptionValue("evtfile"), #indexfiler\
                      Parameters.sarmatrix, \
                      Parameters.edpmatrix, \
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


    def parseOutput(self):
        pass


class GasMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)

    def getRequiredOptions(self):
        return ["outdir", "mapnameprefix", "expmap"]

    def setArguments(self, confDict):

        if not self.allRequiredOptionsSet(confDict, self.getRequiredOptions()):
            self.logger.critical(self,"Some options have not been set.")
            exit(1)

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("mapnameprefix")+".gas.gz"

        self.outfilePath = os.path.join(outDir, outputName)

        self.args = [ expMapGenerator.outfilePath, \
                      self.outfilePath,  \
                      confDict.getOptionValue("skymapL"), \
                      confDict.getOptionValue("skymaH"), \
                    ]


    def parseOutput(self):
        pass


class IntMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)

    def getRequiredOptions(self):
        return ["outdir", "mapnameprefix", "expmap", "ctsmap"]

    def setArguments(self, confDict):

        if not self.allRequiredOptionsSet(confDict, self.getRequiredOptions()):
            self.logger.critical(self,"Some options have not been set.")
            exit(1)

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("mapnameprefix")+".int.gz"
        self.outfilePath = os.path.join(outDir, outputName)


        self.args = [ expMapGenerator.outfilePath, \
                      self.outfilePath,  \
                      ctsMapGenerator.outfilePath, \
                    ]


    def parseOutput(self):
        pass





ctsMapGenerator = CtsMapGenerator("AG_ctsmapgen")
expMapGenerator = ExpMapGenerator("AG_expmapgen")
gasMapGenerator = GasMapGenerator("AG_gasmapgen")
intMapGenerator = IntMapGenerator("AG_intmapgen")
