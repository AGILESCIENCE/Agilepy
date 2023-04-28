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
import numpy as np
from pathlib import Path
from agilepy.core.Parameters import Parameters
from agilepy.utils.ProcessWrapper import ProcessWrapper

class CtsMapGenerator(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)

    def getRequiredOptions(self):
        return ["evtfile", "outdir", "filenameprefix", "energybins", "glat", "glon", "tmin", "tmax"]

    def configureTool(self, config, extraParams=None):

        # self.outputDir = os.path.join(config.getOptionValue("outdir"), "maps")
        self.outputDir = config.getOptionValue("outdir")
        
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
                      np.matrix(config.getOptionValue("energybins")).min(), \
                      np.matrix(config.getOptionValue("energybins")).max(), \
                      config.getOptionValue("fovradmin"), \
                      config.getOptionValue("fovradmax"), \
                    ]





class ExpMapGenerator(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)


    def getRequiredOptions(self):
        return ["logfile", "outdir", "filenameprefix", "energybins", "glat", "glon", "tmin", "tmax"]

    def configureTool(self, config, extraParams=None):

        # self.outputDir = os.path.join(config.getOptionValue("outdir"), "maps")
        self.outputDir = config.getOptionValue("outdir")

        outputName = config.getOptionValue("filenameprefix")+".exp.gz"

        edpmatrix = "None"
        if config.getOptionValue("useEDPmatrixforEXP"):
            edpmatrix = Parameters.getCalibrationMatrices(config.getOptionValue("filtercode"), config.getOptionValue("irf"))[1]

        outfilePath = os.path.join(self.outputDir, outputName)

        self.products = {   
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }

        self.args = [ outfilePath,  \
                      config.getOptionValue("logfile"), # = indexlog
                      Parameters.getCalibrationMatrices(config.getOptionValue("filtercode"), config.getOptionValue("irf"))[0], \
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
                      np.matrix(config.getOptionValue("energybins")).min(), \
                      np.matrix(config.getOptionValue("energybins")).max(), \
                      config.getOptionValue("fovradmin"), \
                      config.getOptionValue("fovradmax"), \
                    ]




class GasMapGenerator(ProcessWrapper):

    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix", "expmap"]

    def configureTool(self, config, extraParams=None):

        self.outputDir = config.getOptionValue("outdir")

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

        self.outputDir = config.getOptionValue("outdir")

        outputName = config.getOptionValue("filenameprefix")+".int.gz"

        outfilePath = os.path.join(self.outputDir, outputName)

        self.products = {
            outfilePath : ProcessWrapper.REQUIRED_PRODUCT
        }

        self.args = [ extraParams["expMapGeneratorOutfilePath"], \
                      outfilePath,  \
                      extraParams["ctsMapGeneratorOutfilePath"], \
                    ]


class Indexgen(ProcessWrapper):
    """
    Thile class generates index file starting from LOG and EVT files

    Args:
        log dir:
        type: EVT | LOG
        out file:
    Usage:
        AG_indexgen <data_dir> <type> <out_file>
    Return:
        indexfile
    """
    
    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)
        self.isAgileTool = False

    def getRequiredOptions(self):
        return ["datadir", "type", "out_file"]

    def configureTool(self, confDict=None, extraParams=None):
        
        self.outputDir = extraParams["out_dir"]
        outputFile = str(Path(self.outputDir).joinpath(extraParams["out_file"]))

        self.args = [extraParams["data_dir"],
                     extraParams["type"],
                     outputFile
                    ]

        self.products = {
            outputFile : ProcessWrapper.REQUIRED_PRODUCT
        }

class Spotfinder(ProcessWrapper):
    """
    This class will call the AG_spotfinder tool.

    Args:
        input file:
        binsize of the input:
        smoothing:
        max number of connected region to found:
        output files:
        algorithm type (int): it selects the algorithm to use: 0 original, 1 new with baricenter calculation, 2 new without baricenter calculation
        remove spot to near: radious, if 0, dont remove
        sky segmentation (optional): 0 - all sky, 1 - b >= 10, 2 - |b|<10, 3 - b <= -10
        shift the result coordinate to north (optional):  true or false (if true, b = b + bin size)
        remove sources outside radius r from the center of the map (default 0, don't remove) (optional)
        exposure file name (optional): default, don't use
        min exposure (optional): default 200
    Usage:
        AG_spotfinder AG_spotfinder MAP.cts.gz 0.5 2 10 MLE0000hypothesis1.multi 1 2 0 0 50.0 MAP.exp.gz 50
    Return:
        
    """
    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)
        self.isAgileTool = False

    def getRequiredOptions(self):
        return ["input_file", "input_binsize", "smoothing", "max_region", "output_files", "algorithm", "remove_spot"]

    def configureTool(self, confDict, extraParams=None):

        self.products = {}

        self.outputDir = confDict.getOptionValue("outdir")

        outputFile = outputFile = str(Path(self.outputDir).joinpath(extraParams["output_files"]))

        self.args = [extraParams["input_file"],
                     extraParams["input_binsize"],
                     extraParams["smoothing"],
                     extraParams["max_region"],
                     outputFile,
                     extraParams["algorithm"],
                     extraParams["remove_spot"]
                    ]
        
        if "sky_segmentation" in extraParams:
            self.args.append(str(extraParams["sky_segmentation"]))

        if "shift_to_north" in extraParams:
            self.args.append(str(extraParams["shift_to_north"]))
        
        if "remove_sources" in extraParams:
            self.args.append(str(extraParams["remove_sources"]))
        
        if "exp_filename" in extraParams:
            self.args.append(str(extraParams["exp_filename"]))
        
        if "min_exp" in extraParams:
            self.args.append(str(extraParams["min_exp"]))

        self.products = {
            outputFile : ProcessWrapper.REQUIRED_PRODUCT,
            outputFile+".reg": ProcessWrapper.REQUIRED_PRODUCT
        }

class Multi(ProcessWrapper):
    """
    This class will call the AG_multi tool. The tool will generate several files, for example:
    
    > ls /agilepy_analysis/vela-xxx_user-xxx_20210217-123618/mle/0/
        analysis_product
        analysis_product.html
        analysis_product.log
        analysis_product_2AGLJ1015-5852.source (optional)
        analysis_product_2AGLJ0835-4514.source (optional)
        analysis_product_2AGLJ1020-5752.source (optional)

    If the sources listed in the sourceLibrary file in AGILE format (e.g. sourceLibrary00001.txt) contains None as first parameter,
    then the corresponding analysis_product_<sourcename>.source will not be produced.
    """
    def __init__(self, exeName, agilepyLogger):
        super().__init__(exeName, agilepyLogger)

    def getRequiredOptions(self):
        return ["outdir", "filenameprefix"]

    def configureTool(self, config, extraParams=None):
        self.products = {}
    
        self.outputDir = config.getOptionValue("outdir")
        
        outfilePath = os.path.join(self.outputDir, config.getOptionValue("filenameprefix"))

        for sourceName in config.getOptionValue("multisources"):
            prodName = outfilePath+"_"+sourceName+".source"
            self.products[prodName] = ProcessWrapper.OPTIONAL_PRODUCT # AG_multi not always produces .source files... (check description)
        
        self.products[outfilePath]         = ProcessWrapper.REQUIRED_PRODUCT
        self.products[outfilePath+".html"] = ProcessWrapper.REQUIRED_PRODUCT
        self.products[outfilePath+".log" ] = ProcessWrapper.REQUIRED_PRODUCT
        
        expratioevaluation = 0
        if config.getOptionValue("expratioevaluation"):
            expratioevaluation = 1  

        calibMatrices = Parameters.getCalibrationMatrices(config.getOptionValue("filtercode"), config.getOptionValue("irf"))


        self.args = [
            config.getOptionValue("maplist"), \
            f"{calibMatrices[0]} {calibMatrices[1]} {calibMatrices[2]}", \
            config.getOptionValue("ranal"), \
            config.getOptionValue("galmode"), \
            config.getOptionValue("isomode"), \
            config.getOptionValue("sourcelist"), \
            # AG_multi tool will add _<sourceName>.source to the outfilePath prefix (for each source)
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
        return ["logfile", "evtfile", "outdir", "filenameprefix", "glat", "glon", "tmin", "tmax"]

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

        edpmatrix = "None"
        if config.getOptionValue("useEDPmatrixforEXP"):
            edpmatrix = Parameters.getCalibrationMatrices(config.getOptionValue("filtercode"), config.getOptionValue("irf"))[1]

        self.args = [ outfilePath,  \
                      config.getOptionValue("logfile"), # = indexlog
                      config.getOptionValue("evtfile"), # = indexfiler
                      Parameters.getCalibrationMatrices(config.getOptionValue("filtercode"), config.getOptionValue("irf"))[0], \
                      edpmatrix, \
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
                      np.matrix(config.getOptionValue("energybins")).min(), \
                      np.matrix(config.getOptionValue("energybins")).max(), \
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
            "-o",
            outfilePath
        ])