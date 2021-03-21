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

from copy import deepcopy
from typing import List
from abc import ABC, abstractmethod

from agilepy.core.CustomExceptions import  SpectrumTypeNotFoundError, \
                              AttributeValueDatatypeNotSupportedError, \
                              SelectionParamNotSupported, \
                              NotFreeableParamsError, \
                              WrongSpatialModelTypeError


from agilepy.core.AgilepyLogger import Color 
from agilepy.utils.AstroUtils import AstroUtils



class Value:
    def __init__(self, name, datatype=None):
        self.name = name
        self.value = None
        self.datatype = datatype

    def set(self, val):
        self.value = self.castTo(val)
        return True

    def get(self, strr=False):
        if strr:
            return str(self.value)
        return self.value

    def castTo(self, val):

        if self.datatype == "int":
            return int(val)
        elif self.datatype == "float":
            return float(val)
        elif self.datatype == "str":
            return str(val)
        elif self.datatype == "List<int>":
            return [int(v) for v in val]
        elif self.datatype == "List<float>":
            return [float(v) for v in val]
        elif self.datatype == "List<str>":
            return [str(v) for v in val]
        elif self.datatype == "tuple<float,float>":
            elem = val.split(",")
            elem[0] = elem[0].replace("(","")
            elem[1] = elem[1].replace(")","")
            glon = float(elem[0].strip())
            glat = float(elem[1].strip())
            return (glon, glat)
        else:
            raise AttributeValueDatatypeNotSupportedError("The datatype {} is not supported for attribute {}".format(self.datatype, self.name))

class OutputVal(Value):
    def __init__(self, name, datatype=None):
        super().__init__(name, datatype)

    def __str__(self):
        return f'\t- {self.name}: {self.value}'

    def setAttributes(self, name=None, value=None):
        if value is not None:
            self.value = self.castTo(value)

class Parameter(Value):
    def __init__(self, name, datatype=None, free=0, scale=None, min=None, max=None, locationLimit=None):
        super().__init__(name, datatype)
        self.free = free
        self.scale = scale
        self.min = min
        self.max = max
        self.locationLimit = locationLimit

    def __str__(self):
        return f'\t- {self.name}: {self.value} free: {self.free}'
        
    def setFree(self, freeVal):
        if self.free == freeVal:
            return False
        else:
            self.free = freeVal
            return True

    def setAttributes(self, name=None, value=None, free=None, scale=None, min=None, max=None, locationLimit=None):
        if value is not None:
            self.value = self.castTo(value)
        if free is not None:
            self.free = int(free)
        if scale is not None:
            self.scale = float(scale)
        if min is not None:
            self.min = float(min)
        if max is not None:
            self.max = float(max)
        if locationLimit is not None:
            self.locationLimit = int(locationLimit)

    def toDict(self):
        d = vars(self)
        outDict = {}
        for k,v in d.items():
            if v is not None and k!="datatype":
                outDict[k] = str(v)

        return outDict

class SourceDescription:

    def set(self, attributeName, attributeVal):
        try:
            parameter = getattr(self, attributeName)
        except AttributeError:
            return False
        return parameter.set(attributeVal)

    def get(self, attributeName, strr=False):
        try:
            parameter = getattr(self, attributeName)
        except AttributeError:
            return None
        return parameter.get(strr=strr) # calling Value's get()

    def setFree(self, attributeName, freeVal):
        try:
            parameter = getattr(self, attributeName)
        except AttributeError:
            return False
        return parameter.setFree(freeVal)

    def getFree(self, attributeName, strr=False):
        freeval = getattr(self, attributeName).free
        #print("freeval: ",freeval)
        #print("attributeName: ",attributeName)
        #print("self",self)
        if strr and freeval is None:
            return "None"
        elif not strr and freeval is None:
            return None
        elif strr and freeval:
            return "1"
        elif strr and not freeval:
            return "0"
        elif not strr and freeval:
            return 1
        elif not strr and not freeval:
            return 0
        else:
            print("Something wrong in getFree()")
            exit(1)


class Spectrum(ABC, SourceDescription):

    @staticmethod
    def getSpectrumParamsNames(stype):

        if stype == "PowerLaw":
            return ["flux", "fluxErr", "index", "indexErr"]

        elif stype == "PLExpCutoff":
            return ["flux", "fluxErr", "index", "indexErr", "cutoffEnergy", "cutoffEnergyErr"]

        elif stype == "PLSuperExpCutoff":
            return ["flux", "fluxErr", "index1", "index1Err", "cutoffEnergy", "cutoffEnergyErr", "index2", "index2Err"]

        elif stype == "LogParabola":
            return ["flux", "fluxErr", "index", "indexErr", "pivotEnergy", "pivotEnergyErr", "curvature", "curvatureErr"]

        else:
            raise SpectrumTypeNotFoundError("Spectrum type '{}' is not supported. Supported spectrum types: ['PowerLaw', 'PLExpCutoff', 'PLSuperExpCutoff', 'LogParabola']".format(stype))


    @staticmethod
    def getSpectrumObject(stype):

        if stype == "PowerLaw":
            return PowerLaw(stype)

        elif stype == "PLExpCutoff":
            return PLExpCutoff(stype)

        elif stype == "PLSuperExpCutoff":
            return PLSuperExpCutoff(stype)

        elif stype == "LogParabola":
            return LogParabola(stype)

        else:
            raise SpectrumTypeNotFoundError("Spectrum type '{}' is not supported. Supported spectrum types: ['PowerLaw', 'PLExpCutoff', 'PLSuperExpCutoff', 'LogParabola']".format(stype))

    @abstractmethod
    def getSpectralIndex(self):
        pass

    def __init__(self, stype):
        self.stype = stype
        self.flux = Parameter("flux", "float", free = 0)
        self.fluxErr = OutputVal("flux", "float")

class PowerLaw(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.index = Parameter("index", "float", free=0, scale=-1.0, min=0.5, max=5)
        self.indexErr = OutputVal("indexErr", "float")

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index.toDict()]

    def getSpectralIndex(self):
        return self.index.value

    def getParameters(self):
        return {
            "flux(ph/cm2s)" : (self.flux.value, self.fluxErr.value),
            "index" : (self.index.value,self.indexErr.value)
        }

class PLExpCutoff(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.index = Parameter("index", "float", free=0, scale=-1.0, min=0.5, max=5)
        self.cutoffEnergy = Parameter("cutoffEnergy", "float", free=0, scale=-1.0, min=20, max=10000)
        self.cutoffEnergyErr = OutputVal("cutoffEnergyErr", "float")

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index}\n{self.cutoffEnergy}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index.toDict(), self.cutoffEnergy.toDict()]

    def getSpectralIndex(self):
        return self.index.value

    def getParameters(self):
        return {
            "flux(ph/cm2s)" : (self.flux.value, self.fluxErr.value),
            "cutoffEnergy" : (self.cutoffEnergy.value, self.cutoffEnergyErr.value)
        }

class PLSuperExpCutoff(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.index1 = Parameter("index1", "float", free=0, scale=-1.0, min=0.5, max=5)
        self.index1Err = OutputVal("index1Err", "float")
        self.cutoffEnergy = Parameter("cutoffEnergy", "float", free=0, scale=-1.0, min=20, max=10000)
        self.cutoffEnergyErr = OutputVal("cutoffEnergyErr", "float")
        self.index2 = Parameter("index2", "float", free=0, scale=-1.0, min=0, max=100)
        self.index2Err = OutputVal("index2Err", "float")

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index1}\n{self.cutoffEnergy}\n{self.index2}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index1.toDict(), self.cutoffEnergy.toDict(), self.index2.toDict()]

    def getSpectralIndex(self):
        return self.index1.value

    def getParameters(self):
        return {
            "flux(ph/cm2s)" : (self.flux.value, self.fluxErr.value),
            "cutoffEnergy" : (self.cutoffEnergy.value, self.cutoffEnergyErr.value),
            "index1" : (self.index1.value, self.index1Err.value),
            "index2" : (self.index2.value, self.index2Err.value)
        }

class LogParabola(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.index = Parameter("index", "float", free=0, scale=-1.0, min=1, max=4)
        self.indexErr = OutputVal("indexErr", "float")
        self.pivotEnergy = Parameter("pivotEnergy", "float", free=0, scale=-1.0, min=500, max=3000)
        self.pivotEnergyErr = OutputVal("pivotEnergyErr", "float")
        self.curvature = Parameter("curvature", "float", free=0, scale=-1.0, min=0.1, max=3)
        self.curvatureErr = OutputVal("curvatureErr", "float")

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index}\n{self.pivotEnergy}\n{self.curvature}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index.toDict(), self.pivotEnergy.toDict(), self.curvature.toDict()]

    def getSpectralIndex(self):
        return self.index.value

    def getParameters(self):
        return {
            "flux(ph/cm2s)" : (self.flux.value, self.fluxErr.value),
            "index" : (self.index.value, self.indexErr.value),
            "pivotEnergy" : (self.pivotEnergy.value, self.pivotEnergyErr.value),
            "curvature" : (self.curvature.value, self.curvatureErr.value)
        }

class SpatialModel(SourceDescription):

    @staticmethod
    def getSpatialModelObject(type, ll):

        if type not in ["PointSource"]:

            raise WrongSpatialModelTypeError(f"SpatialModel '{type}' is not supported. Supported SpatialModel types: ['PointSource']")

        return PointSourceSpatialModel(type, ll)


    def __init__(self, sptype, ll):
        self.sptype = sptype
        self.locationLimit = ll

class PointSourceSpatialModel(SpatialModel):
    def __init__(self, type, ll):
        super().__init__(type, ll)
        self.pos = Parameter("pos", "tuple<float,float>")
        self.dist = OutputVal("dist", "float")

    def __str__(self):
        return f'\n - SpatialModel type: {self.sptype}\n{self.pos}\n{self.dist}'

    def getParameterDict(self):
        return [self.pos.toDict()]

class MultiOutput(SourceDescription):
    def __init__(self):

        self.name = OutputVal("name", "str")

        self.multiSqrtTS = OutputVal("multiSqrtTS", "float")

        self.multiFix = OutputVal("multiFix", "float")
        self.multiindex = OutputVal("multiindex", "float")
        self.multiULConfidenceLevel = OutputVal("multiULConfidenceLevel", "float")
        self.multiSrcLocConfLevel = OutputVal("multiSrcLocConfLevel", "float")

        self.multiFlux = OutputVal("multiFlux", "float")
        self.multiFluxErr = OutputVal("multiFluxErr", "float")
        self.multiFluxPosErr = OutputVal("multiFluxPosErr", "float")
        self.multiFluxNegErr = OutputVal("multiFluxNegErr", "float")

        self.multiStartFlux = OutputVal("multiStartFlux", "float")
        self.multiTypefun = OutputVal("multiTypefun", "float")
        self.multipar2 = OutputVal("multipar2", "float")
        self.multipar3 = OutputVal("multipar3", "float")
        self.multiGalmode2 = OutputVal("multiGalmode2", "float")
        self.multiGalmode2fit = OutputVal("multiGalmode2fit", "float")
        self.multiIsomode2 = OutputVal("multiIsomode2", "float")
        self.multiIsomode2fit = OutputVal("multiIsomode2fit", "float")
        self.multiEdpcor = OutputVal("multiEdpcor", "float")
        self.multiFluxcor = OutputVal("multiFluxcor", "float")
        self.multiIntegratorType = OutputVal("multiIntegratorType", "float")
        self.multiExpratioEval = OutputVal("multiExpratioEval", "float")
        self.multiExpratioMinthr = OutputVal("multiExpratioMinthr", "float")
        self.multiExpratioMaxthr = OutputVal("multiExpratioMaxthr", "float")
        self.multiExpratioSize = OutputVal("multiExpratioSize", "float")


        self.multiUL = OutputVal("multiUL", "float")

        self.multiExp = OutputVal("multiExp", "float")


        self.multiErgLog = OutputVal("multiErgLog", "float")
        self.multiErgLogErr = OutputVal("multiErgLogErr", "float")
        self.multiErgLogUL = OutputVal("multiErgLogUL", "float")


        self.multiStartL = OutputVal("multiStartL", "float")
        self.multiStartB = OutputVal("multiStartB", "float")

        self.multiDist = OutputVal("multiDist", "float")

        self.multiLPeak = OutputVal("multiLPeak", "float")
        self.multiBPeak = OutputVal("multiBPeak", "float")
        self.multiDistFromStartPositionPeak = OutputVal("multiDistFromStartPositionPeak", "float")

        self.multiL = OutputVal("multiL", "float")
        self.multiB = OutputVal("multiB", "float")
        self.multiDistFromStartPosition = OutputVal("multiDistFromStartPosition", "float")
        self.multir = OutputVal("multir", "float")
        self.multia = OutputVal("multia", "float")
        self.multib = OutputVal("multib", "float")
        self.multiphi = OutputVal("multiphi", "float")

        self.multiCounts = OutputVal("multiCounts", "float")
        self.multiCountsErr = OutputVal("multiCountsErr", "float")

        self.multiIndex = OutputVal("multiIndex", "float")
        self.multiIndexErr = OutputVal("multiIndexErr", "float")

        self.multiPar2 = OutputVal("multiPar2", "float")
        self.multiPar2Err = OutputVal("multiPar2Err", "float")

        self.multiPar3 = OutputVal("multiPar3", "float")
        self.multiPar3Err = OutputVal("multiPar3Err", "float")

        self.multiGalCoeff = OutputVal("multiGalCoeff", "List<float>")
        self.multiGalErr = OutputVal("multiGalErr", "List<float>")

        self.multiIsoCoeff = OutputVal("multiIsoCoeff", "List<float>")
        self.multiIsoErr = OutputVal("multiIsoErr", "List<float>")

        self.startDataTT = OutputVal("startDataTT", "float")
        self.endDataTT = OutputVal("endDataTT", "float")

        self.multiEmin = OutputVal("multiEmin", "List<float>")
        self.multiEmax = OutputVal("multiEmax", "List<float>")
        self.multifovmin = OutputVal("multifovmin", "List<float>")
        self.multifovmax = OutputVal("multifovmax", "List<float>")
        self.multialbedo = OutputVal("multialbedo", "float")
        self.multibinsize = OutputVal("multibinsize", "float")
        self.multiexpstep = OutputVal("multiexpstep", "float")
        self.multiphasecode = OutputVal("multiphasecode", "float")

        self.multiExpRatio = OutputVal("multiExpRatio", "float")

    def __str__(self):
        return f'\n - SpatialModel\n{self.multiSqrtTS}\n{self.multiFlux}\n{self.multiFluxErr}\n{self.multiUL}\n{self.multiDist} \
                 \n{self.multiStartL}\n{self.multiStartB}\n{self.multiL}\n{self.multiB}\n{self.multiDist}'




class Source:

    selectionParams = {
        "source": {
            "name": ["name", "Name", "NAME"],
            "dist": ["dist", "Dist", "DIST"],
            "flux": ["flux", "Flux", "FLUX"]
        },
        "multi": {
            "sqrtts" : ["sqrt_ts", "sqrtts", "sqrtTS", "SqrtTS", "SQRTTS"]
        }
    }

    freeParams = {
        "spectrum": ["flux", "index", "index1", "index2", "cutoffEnergy", "pivotEnergy", "curvature", "index2"],
        "spatialModel": ["pos"]


    }


    mapping = {
        "flux" : "multiFlux",
        "fluxErr" : "multiFluxErr",
        "index" : "multiIndex",
        "indexErr" : "multiIndexErr",
        "index1" : "multiIndex",
        "index1Err" : "multiIndexErr",
        "cutoffEnergy" : "multiPar2",
        "cutoffEnergyErr" : "multiPar2Err",
        "pivotEnergy" : "multiPar2",
        "pivotEnergyErr" : "multiPar2Err",
        "index2" : "multiPar3",
        "index2Err" : "multiPar3Err",
        "curvature" : "multiPar3",
        "curvatureErr" : "multiPar3Err"
    }

    def getSourceDistanceFromLB(self, l, b):

        if self.multi:

            sourceL = self.multi.get("multiL")
            sourceB = self.multi.get("multiB")

            if sourceL == -1:
                sourceL = self.multi.get("multiStartL")

            if sourceB == -1:
                sourceB = self.multi.get("multiStartB")

        else:
            pos = self.spatialModel.get("pos")
            sourceL = pos[0]
            sourceB = pos[1]

        return AstroUtils.distance(sourceL, sourceB, l, b)



    def saveMultiAnalysisResults(self, mapCenterL, mapCenterB):
        stype = type(self.spectrum).__name__
        paramsToUpdate = Spectrum.getSpectrumParamsNames(stype)
        
        # spectrum
        if self.multi:
            for paramName in paramsToUpdate:
                multiParamName = Source.mapping[paramName]
                multiParamValue = self.multi.get(multiParamName)
                if multiParamValue is not None:
                    self.initialSpectrum.set(paramName, multiParamValue)

        # position
        if self.multi:
            newPos = Parameter("pos", "tuple<float,float>")
            newPos.setAttributes(value = f"({self.multi.multiLPeak.value}, {self.multi.multiBPeak.value})", free = self.spatialModel.pos.free)
            self.initialSpatialModel.pos = newPos

            newDistance = self.getSourceDistanceFromLB(mapCenterL, mapCenterB)
            self.initialSpatialModel.dist.setAttributes(value = newDistance)






    def __init__(self, name, type):
        self.name = name
        self.type = type

        self.initialSpatialModel = None
        self.initialSpectrum = None

        self.spatialModel = None
        self.spectrum = None
        
        self.multi = None

        self.intitialized = False

    def setInitialAttributes(self):
        if not self.intitialized:
            self.initialSpatialModel = deepcopy(self.spatialModel)
            self.initialSpectrum = deepcopy(self.spectrum)
        self.intitialized = True

    def getFreeParams(self):
        return [k for k,v in vars(self.spectrum).items() if isinstance(v, Parameter) and self.spectrum.getFree(k) > 0] + \
                    [k for k,v in vars(self.spatialModel).items() if isinstance(v, Parameter) and self.spatialModel.getFree(k) > 0]


    def bold(self, ss):
        return Color.BOLD + ss + Color.END

    def colorRed(self, ss):
        return Color.RED + ss + Color.END

    def colorBlue(self, ss):
        return Color.BLUE + ss + Color.END

    
    def __str__title(self):
        strr = '\n-----------------------------------------------------------'
        strr += self.bold(f'\n Source name: {self.name} ({self.type})')
        if self.multi:
            strr += self.bold(" => sqrt(ts): "+str(self.multi.get("multiSqrtTS")))
        return strr        

    def __str__freeParams(self):
        freeParams = self.getFreeParams()
        if len(freeParams) == 0:
            return f'\n  * {self.bold("Free parameters")}: none'
        else:
            return f'\n  * {self.bold("Free parameters")}: '+' '.join(freeParams)




    def __str__sourcePos(self):

        print(self.initialSpatialModel.get("dist"))
        print(self.initialSpatialModel.get("pos"))

    def __str__sourceParams(self):
        strR = ''
        strR += f'\n  * {self.bold("Initial source parameters")}: ({self.initialSpectrum.stype})'


        spectrumParams = Spectrum.getSpectrumParamsNames(self.initialSpectrum.stype)

        for i, paramName in enumerate(spectrumParams):
            
            # end of the list
            if i+1 == len(spectrumParams):
                break
            
            # print only params not errors
            if i % 2 == 0:
                pn = paramName
                if paramName == "flux":
                    pn += "(ph/cm2s)"
                strR += f"\n\t- {pn}: {str(self.initialSpectrum.get(paramName))}"
                if self.initialSpectrum.get(spectrumParams[i+1]):
                    strR += f" +/- {str(self.initialSpectrum.get(spectrumParams[i+1]))}"

        strR += f"\n\t- Source position: {self.initialSpatialModel.get('pos')} (l,b)"
        strR += f"\n\t- Distance from map center: {round(self.initialSpatialModel.get('dist'), 4)} deg"

        return strR

    def __str__multiAnalisys(self):
        strr = ''
        if self.multi is None:
            return strr

        # freeParams = self.getFreeParams()

        ## Multi
        if self.multi:

            strr = f'\n  * {self.bold("Last MLE analysis")}:'
            
            # spectrum parameters
            for key,val in self.spectrum.getParameters().items():
                strr += f'\n\t- {key}: {val[0]}'
                if val[1]:
                    strr += f" +/- {val[1]}"
            
            # ag_multi parameters
            strr += f'\n\t- upper limit(ph/cm2s): {self.multi.get("multiUL")}'
            strr += f'\n\t- ergLog(erg/cm2s): {self.multi.get("multiErgLog")}'
            if self.multi.get("multiErgLogErr"):
                strr += f' +/- {self.multi.get("multiErgLogErr")}'
            strr += f'\n\t- galCoeff: {self.multi.get("multiGalCoeff")}'
            if self.multi.get("multiGalErr") and sum(self.multi.get("multiGalErr")) != 0:
                strr += f' +/- {self.multi.get("multiGalErr")}'
            strr += f'\n\t- isoCoeff: {self.multi.get("multiIsoCoeff")}' 
            if self.multi.get("multiIsoErr") and sum(self.multi.get("multiIsoErr")) != 0:
                strr += f' +/- {self.multi.get("multiIsoErr")}'
            strr += f'\n\t- exposure(cm2s): {self.multi.get("multiExp")}'
            strr += f'\n\t- exp-ratio: {self.multi.get("multiExpRatio")}'
            strr += f'\n\t- L_peak: {self.multi.get("multiLPeak")}'
            strr += f'\n\t- B_peak: {self.multi.get("multiBPeak")}'
            strr += f'\n\t- Distance from start pos: {self.multi.get("multiDistFromStartPositionPeak")}'
            strr += f'\n\t- position:'
            strr += f'\n\t    - L: {self.multi.get("multiL")}'
            strr += f'\n\t    - B: {self.multi.get("multiB")}'
            strr += f'\n\t    - Distance from start pos: {self.multi.get("multiDistFromStartPosition")}'
            strr += f'\n\t    - radius of circle: {self.multi.get("multir")}'
            strr += f'\n\t    - ellipse:'
            strr += f'\n\t\t  - a: {self.multi.get("multia")}'
            strr += f'\n\t\t  - b: {self.multi.get("multib")}'
            strr += f'\n\t\t  - phi: {self.multi.get("multiphi")}'


        strr += '\n-----------------------------------------------------------'
        return strr
        
    
    def __str__(self):
        strr = ''
        strr += self.__str__title()
        strr += self.__str__freeParams()
        strr += self.__str__sourceParams()
        strr += self.__str__multiAnalisys()
        return strr

    def getSpectralIndex(self):
        return self.spectrum.getSpectralIndex()

    def getFlux(self):
        return self.spectrum.get("flux")

    def setFlux(self, val):
        return self.spectrum.set("flux", val)

    def getSelectionValue(self, paramName):

        if paramName == "name":
            return self.name

        elif paramName == "flux":
            if self.multi:
                return self.multi.get("multiFlux")
            else:
                return self.spectrum.get("flux")

        elif paramName == "dist":
            if self.multi:
                return self.multi.get("multiDist")
            else:
                return self.spatialModel.get("dist")

        elif paramName == "multiSqrtTS":
            return self.multi.get("multiSqrtTS")

        else:
            return None


    def isCompatibleWith(self, paramName):
        if paramName in Source._getSelectionParams(onlyMultiParams=True) and self.multi is None:
            return False
        else:
            return True

    @staticmethod
    def _mapSelectionParams(userSelectionParams):
        """
        Raise exception if at least one param is not supported
        """
        mappedUserSelectionParams = {}

        for userParam in userSelectionParams:

            if userParam in Source.selectionParams["source"]["name"]:

                mappedUserSelectionParams[userParam] = "name"

            elif userParam in Source.selectionParams["source"]["dist"]:

                mappedUserSelectionParams[userParam] = "dist"

            elif userParam in Source.selectionParams["source"]["flux"]:

                mappedUserSelectionParams[userParam] = "flux"

            elif userParam in Source.selectionParams["multi"]["sqrtts"]:

                mappedUserSelectionParams[userParam] = "multiSqrtTS"

            else:
                error_msg = "The selectionParam {} is not supported and it is not going to be used. Supported params: [name, dist, flux, sqrtts]".format(userParam)

                raise SelectionParamNotSupported(error_msg)

        return mappedUserSelectionParams

    @staticmethod
    def _getSelectionParams(onlyMultiParams = False):
        sparams = []
        if onlyMultiParams:
            for _,v in Source.selectionParams["multi"].items():
                sparams += v
        else:
            for _,v in Source.selectionParams["source"].items():
                sparams += v
        return sparams

    @staticmethod
    def _getFreeParams():
        fparams = []
        fparams += Source.freeParams["spectrum"]
        fparams += Source.freeParams["spatialModel"]
        return fparams

    def setFreeAttributeValueOf(self, parameterName, freeval):

        freeable = Source._getFreeParams()

        if parameterName not in freeable:
            warning_msg = 'The parameter %s cannot be released! You can set "free" to: %s'%(parameterName, ' '.join(freeable))
            raise NotFreeableParamsError(warning_msg)

        if parameterName in Source.freeParams["spectrum"]:
            isChanged = self.spectrum.setFree(parameterName, freeval)
        else:
            isChanged = self.spatialModel.setFree(parameterName, freeval)

        return isChanged
