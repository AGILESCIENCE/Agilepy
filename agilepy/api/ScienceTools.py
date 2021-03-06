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

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)

    def getRequiredOptions(self):
        return ["evtfile", "outdir", "filenameprefix", "emin", "emax", "energybins", "glat", "glon", "tmin", "tmax"]

    def configureTool(self, config, extraParams=None):

        self.outputDir = os.path.join(config.getOptionValue("outdir"), "maps")
        outputName = config.getOptionValue("filenameprefix")+".cts.gz"

        outfilePath = os.path.join(self.outputDir, outputName)

        self.products = {   
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }
        self.args = [ outfilePath,  \
                      config.getOptionValue("evtfile"), # = indexfilter 
                      config.getOptionValue("timelist"), \
                      config.getOptionValue("mapsize"), \
                      config.getOptionValue("binsize"), \
                      config.getOptionValue("glon"), \
                      config.getOptionValue("glat"), \
                      config.getOptionValue("lonpole"), \
                      config.getOptionValue("albedorad"), \
                      config.getOptionValue("phasecode"), \
                      config.getOptionValue("filtercode"), \
                      config.getOptionValue("proj"), \
                      config.getOptionValue("tmin"), \
                      config.getOptionValue("tmax"), \
                      config.getOptionValue("emin"), \
                      config.getOptionValue("emax"), \
                      config.getOptionValue("fovradmin"), \
                      config.getOptionValue("fovradmax"), \
                    ]





class ExpMapGenerator(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)


    def getRequiredOptions(self):
        return ["logfile", "outdir", "filenameprefix", "emin", "emax", "glat", "glon", "tmin", "tmax"]

    def configureTool(self, config, extraParams=None):

        self.outputDir = os.path.join(config.getOptionValue("outdir"), "maps")
        outputName = config.getOptionValue("filenameprefix")+".exp.gz"

        edpmatrix = "None"
        if config.getOptionValue("useEDPmatrixforEXP"):
            edpmatrix = Parameters.edpmatrix

        outfilePath = os.path.join(self.outputDir, outputName)

        self.products = {   
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }

        self.args = [ outfilePath,  \
                      config.getOptionValue("logfile"), # = indexlog
                      Parameters.sarmatrix, \
                      edpmatrix, \
                      config.getOptionValue("maplistgen"), \
                      config.getOptionValue("timelist"), \
                      config.getOptionValue("mapsize"), \
                      config.getOptionValue("binsize"), \
                      config.getOptionValue("glon"), \
                      config.getOptionValue("glat"), \
                      config.getOptionValue("lonpole"), \
                      config.getOptionValue("albedorad"), \
                      0.5, \
                      360, \
                      5.0, \
                      config.getOptionValue("phasecode"), \
                      config.getOptionValue("proj"), \
                      config.getOptionValue("expstep"), \
                      config.getOptionValue("timestep"), \
                      config.getOptionValue("spectralindex"), \
                      config.getOptionValue("tmin"), \
                      config.getOptionValue("tmax"), \
                      config.getOptionValue("emin"), \
                      config.getOptionValue("emax"), \
                      config.getOptionValue("fovradmin"), \
                      config.getOptionValue("fovradmax"), \
                    ]




class GasMapGenerator(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix", "expmap"]

    def configureTool(self, config, extraParams=None):

        self.outputDir = os.path.join(config.getOptionValue("outdir"), "maps")
        outputName = config.getOptionValue("filenameprefix")+".gas.gz"

        outfilePath = os.path.join(self.outputDir, outputName)

        self.products = {
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }

        self.args = [ extraParams["expMapGeneratorOutfilePath"], \
                      outfilePath,  \
                      config.getOptionValue("skymapL"), \
                      config.getOptionValue("skymapH"), \
                    ]




class IntMapGenerator(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix", "expmap", "ctsmap"]

    def configureTool(self, config, extraParams=None):

        self.outputDir = os.path.join(config.getOptionValue("outdir"), "maps")
        outputName = config.getOptionValue("filenameprefix")+".int.gz"
        outfilePath = os.path.join(self.outputDir, outputName)

        self.products = {
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }

        self.args = [ extraParams["expMapGeneratorOutfilePath"], \
                      outfilePath,  \
                      extraParams["ctsMapGeneratorOutfilePath"], \
                    ]






class Multi(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix"]

    def configureTool(self, config, extraParams=None):

        self.outputDir = os.path.join(config.getOptionValue("outdir"), "mle")
        outputName = config.getOptionValue("filenameprefix")+(str(self.callCounter).zfill(4))
        outfilePath = os.path.join(self.outputDir, outputName)

        for sourceName in config.getOptionValue("multisources"):
            prodName = os.path.join(self.outputDir, outputName+"_"+sourceName+".source")
            self.products[prodName] = ProcessWrapper.REQUIRED_PRODUCT

        expratioevaluation = 0
        if config.getOptionValue("expratioevaluation"):
            expratioevaluation = 1


        self.args = [
            config.getOptionValue("maplist"), \
            Parameters.matrixconf, \
            config.getOptionValue("ranal"), \
            config.getOptionValue("galmode"), \
            config.getOptionValue("isomode"), \
            config.getOptionValue("sourcelist"), \
            outfilePath, \
            config.getOptionValue("ulcl"), \
            config.getOptionValue("loccl"), \
            config.getOptionValue("galmode2"), \
            config.getOptionValue("galmode2fit"), \
            config.getOptionValue("isomode2"), \
            config.getOptionValue("isomode2fit"), \
            config.getOptionValue("edpcorrection"), \
            config.getOptionValue("fluxcorrection"), \
            config.getOptionValue("minimizertype"), \
            config.getOptionValue("minimizeralg"), \
            config.getOptionValue("minimizerdefstrategy"), \
            config.getOptionValue("mindefaulttolerance"), \
            config.getOptionValue("integratortype"), \
            expratioevaluation, \
            config.getOptionValue("expratio_minthr"), \
            config.getOptionValue("expratio_maxthr"), \
            config.getOptionValue("expratio_size"), \
            config.getOptionValue("contourpoints"),
        ]




class AP(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)

    def getRequiredOptions(self):
        return ["logfile", "evtfile", "outdir", "filenameprefix", "emin", "emax", "glat", "glon", "tmin", "tmax"]

    def configureTool(self, config, extraParams=None):
        """
        This method must initialize the 'args', 'products' and 'outputDir' attributes of the object.
        """

        self.outputDir = os.path.join(config.getOptionValue("outdir"), "ap")
        outputName = config.getOptionValue("filenameprefix")

        outfilePath = os.path.join(self.outputDir, outputName)

        self.products = {
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT,
            outfilePath+".ph" : ProcessWrapper.OPTIONAL_PRODUCT
        }

        self.args = [ outfilePath,  \
                      config.getOptionValue("logfile"), # = indexlog
                      config.getOptionValue("evtfile"), # = indexfiler
                      Parameters.sarmatrix, \
                      Parameters.edpmatrix, \
                      config.getOptionValue("timelist"), \
                      config.getOptionValue("binsize"), \
                      config.getOptionValue("radius"), \
                      config.getOptionValue("glon"), \
                      config.getOptionValue("glat"), \
                      config.getOptionValue("lonpole"), \
                      config.getOptionValue("albedorad"), \
                      0.5, \
                      360.0, \
                      5.0, \
                      config.getOptionValue("phasecode"), \
                      config.getOptionValue("timestep"), \
                      config.getOptionValue("spectralindex"), \
                      config.getOptionValue("tmin"), \
                      config.getOptionValue("tmax"), \
                      config.getOptionValue("emin"), \
                      config.getOptionValue("emax"), \
                      config.getOptionValue("fovradmin"), \
                      config.getOptionValue("fovradmax"), \
                      config.getOptionValue("filtercode"), \
                      config.getOptionValue("timeslot")
                    ]


class Cwt2(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)
        self.isAgileTool = False

    
    def getRequiredOptions(self):
        return ["ctsmap", "outputdir", "filenameprefix"]

    def configureTool(self, config, extraParams=None):

        self.outputDir = os.path.join(config.getOptionValue("outdir"), "wavelet_analysis/cwt2")
        
        outputName = config.getOptionValue("filenameprefix")
        outfilePath = os.path.join(self.outputDir, outputName+"_CWT2"+".wtf")

        self.products = {
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }

        self.args = [
            "-v -w log -s",
            str(config.getOptionValue("scaletype"))+":"+str(config.getOptionValue("scalenum"))+":"+str(config.getOptionValue("scalemin"))+":"+str(config.getOptionValue("scalemax")),
            "-i",
            config.getOptionValue("ctsmap"),
            "-o",
            outfilePath
            ]

class Met(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)
        self.isAgileTool = False

    
    def getRequiredOptions(self):
        return ["outputdir", "filenameprefix"]

    def configureTool(self, config, extraParams=None):
        
        self.outputDir = os.path.join(config.getOptionValue("outdir"), "wavelet_analysis/met")
        outputName = config.getOptionValue("filenameprefix")
        outfilePath = os.path.join(self.outputDir, outputName+"_MET"+".met")

        self.products = {
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }

        self.args = [
            "-v -n",
            config.getOptionValue("methistsize"),
            "-i",
            extraParams["Cwt2OutfilePath"][0],
            "-o",
            outfilePath
            ]


class Ccl(ProcessWrapper):
    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)
        self.isAgileTool = False

    def getRequiredOptions(self):
        return ["outputprefix", "filenameprefix"]

    def configureTool(self, config, extraParams=None):

        self.outputDir = os.path.join(config.getOptionValue("outdir"), "wavelet_analysis/ccl")
        outputName = config.getOptionValue("filenameprefix")
        outfilePath = os.path.join(self.outputDir, outputName+"_CCL"+".list")

        self.products = {
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }

        self.args = ["-v"]

        if (float(config.getOptionValue("cclsizemin")) != -1)  or (float(config.getOptionValue("cclsizemax")) != -1):
            self.args.extend([
                "-c",
                str(config.getOptionValue("cclsizemin"))+":"+str(config.getOptionValue("cclsizemax")),
                ])
        
        if (float(config.getOptionValue("cclradmin")) != -1) or (float(config.getOptionValue("cclradmax") != -1)):
            self.args.extend([
                "-r",
                str(config.getOptionValue("cclradmin"))+":"+str(config.getOptionValue("cclradmax"))
            ])

        if (float(config.getOptionValue("cclscalemin")) != -1) or (float(config.getOptionValue("cclscalemax")) != -1):
            self.args.extend([
                "-s",
                str(config.getOptionValue("cclscalemin"))+":"+str(config.getOptionValue("cclscalemax"))
            ])

        self.args.extend([
            "-i",
            extraParams["MetOutfilePath"][0],
            ">",
            outfilePath
        ])





    

    
    
    







