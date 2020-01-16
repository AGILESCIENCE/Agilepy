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
from agilepy.dataclasses.Source import MultiOutput

class CtsMapGenerator(ProcessWrapper):

    def __init__(self, exeName, parseOutput = False):
        super().__init__(exeName, parseOutput)

    def getRequiredOptions(self):
        return ["evtfile", "outdir", "filenameprefix", "emin", "emax", "energybins", "glat", "glon", "tmin", "tmax"]

    def setArguments(self, confDict):

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("filenameprefix")+".cts.gz"

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


    def parseOutputFile(self):
        pass



class ExpMapGenerator(ProcessWrapper):

    def __init__(self, exeName, parseOutput = False):
        super().__init__(exeName, parseOutput)


    def getRequiredOptions(self):
        return ["logfile", "outdir", "filenameprefix", "emin", "emax", "glat", "glon", "tmin", "tmax"]

    def setArguments(self, confDict):

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("filenameprefix")+".exp.gz"

        edpmatrix = "None"
        if confDict.getOptionValue("useEDPmatrixforEXP"):
            edpmatrix = Parameters.edpmatrix

        self.outfilePath = os.path.join(outDir, outputName)

        self.args = [ self.outfilePath,  \
                      confDict.getOptionValue("logfile"), #indexfiler\
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


    def parseOutputFile(self):
        pass


class GasMapGenerator(ProcessWrapper):

    def __init__(self, exeName, parseOutput = False):
        super().__init__(exeName, parseOutput)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix", "expmap"]

    def setArguments(self, confDict):

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("filenameprefix")+".gas.gz"

        self.outfilePath = os.path.join(outDir, outputName)

        self.args = [ expMapGenerator.outfilePath, \
                      self.outfilePath,  \
                      confDict.getOptionValue("skymapL"), \
                      confDict.getOptionValue("skymaH"), \
                    ]


    def parseOutputFile(self):
        pass


class IntMapGenerator(ProcessWrapper):

    def __init__(self, exeName, parseOutput = False):
        super().__init__(exeName, parseOutput)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix", "expmap", "ctsmap"]

    def setArguments(self, confDict):

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("filenameprefix")+".int.gz"
        self.outfilePath = os.path.join(outDir, outputName)


        self.args = [ expMapGenerator.outfilePath, \
                      self.outfilePath,  \
                      ctsMapGenerator.outfilePath, \
                    ]


    def parseOutputFile(self):
        pass




class Multi(ProcessWrapper):

    def __init__(self, exeName, parseOutput = False):
        super().__init__(exeName, parseOutput)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix"]

    def setArguments(self, confDict):

        outDir = confDict.getOptionValue("outdir")
        outputName = confDict.getOptionValue("filenameprefix")
        self.outfilePath = os.path.join(outDir, outputName)

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


    def parseOutputFile(self):

        # self.logger.info(self, "Parsing output file of AG_multi: %s", [self.outfilePath])

        with open(self.outfilePath, 'r') as sf:
            lines = sf.readlines()

        body = [line for line in lines if line[0] != "!"]
        assert 17==len(body)


        allValues = []

        for lin_num,line in enumerate(body):

            values = line.split(" ")

            values = [v.strip() for v in values if v!='']

            if lin_num == 0:
                values = [v for v in values if v!='[' and v!=']' and v!=',']

            elif lin_num == 5:
                fluxperchannel = values[-1].split(",")
                values = [*values[:-1], fluxperchannel]

            elif lin_num == 8:
                galcoeffs  = line.split(" ")[0].split(",")
                galcoeffserr = [g.strip() for g in line.split(" ")[1].split(",")]
                values = [galcoeffs, galcoeffserr]

            elif lin_num == 9:
                galzerocoeffs  = line.split(" ")[0].split(",")
                galzerocoeffserr = [g.strip() for g in line.split(" ")[1].split(",")]
                values = [galzerocoeffs, galzerocoeffserr]

            elif lin_num == 10:
                isocoeffs  = line.split(" ")[0].split(",")
                isocoeffserr = [g.strip() for g in line.split(" ")[1].split(",")]
                values = [isocoeffs, isocoeffserr]

            elif lin_num == 11:
                isozerocoeffs  = line.split(" ")[0].split(",")
                isozerocoeffserr = [g.strip() for g in line.split(" ")[1].split(",")]
                values = [isozerocoeffs, isozerocoeffserr]

            elif lin_num == 13:
                energybins = line.split(" ")[0].split(",")
                emins = [e.split("..")[0] for e in energybins]
                emaxs = [e.split("..")[1] for e in energybins]
                fovbinnumbers = line.split(" ")[1].split(",")
                fovmin = [e.split("..")[0] for e in fovbinnumbers]
                fovmax = [e.split("..")[1] for e in fovbinnumbers]
                values = [emins, emaxs, fovmin, fovmax, *values[-5:]]


            # print("LINE %d ELEMENTS %d"%(lin_num, len(values)))
            allValues += values

        #print("allValues: ", allValues)
        #print("allValues sum: ", len(allValues))

        return MultiOutput(*allValues)


ctsMapGenerator = CtsMapGenerator("AG_ctsmapgen")
expMapGenerator = ExpMapGenerator("AG_expmapgen")
gasMapGenerator = GasMapGenerator("AG_gasmapgen")
intMapGenerator = IntMapGenerator("AG_intmapgen")

multi = Multi("AG_multi", parseOutput=True)
