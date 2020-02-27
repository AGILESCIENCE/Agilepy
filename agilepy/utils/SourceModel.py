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


from dataclasses import dataclass
from typing import List
import datetime
import inspect
from agilepy.utils.CustomExceptions import SpectrumTypeNotFoundError, \
                                           AttributeValueDatatypeNotSupportedError, \
                                           SelectionParamNotSupported, \
                                           NotFreeableParamsError

class Value:
    def __init__(self, name, datatype=None):
        self.name = name
        self.value = None
        self.datatype = datatype

    def set(self, val):
        self.value = self.castTo(val)
        return True

    def get(self, strRepr=True):
        if strRepr:
            return str(self.value)
        else:
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
        parameter.set(attributeVal)

    def get(self, attributeName, strRepr = False):
        try:
            parameter = getattr(self, attributeName)
        except AttributeError:
            return False
        return parameter.get(strRepr) # calling Value's get()

    def setFree(self, attributeName, freeVal):
        try:
            parameter = getattr(self, attributeName)
        except AttributeError:
            return False
        return parameter.setFree(freeVal)

    def getFree(self, attributeName, strRepr=False):
        freeval = getattr(self, attributeName).free
        #print("freeval: ",freeval)
        #print("attributeName: ",attributeName)
        #print("self",self)
        #input(".")
        if strRepr and freeval is None:
            return "None"
        elif not strRepr and freeval is None:
            return None
        elif strRepr and freeval:
            return "1"
        elif strRepr and not freeval:
            return "0"
        elif not strRepr and freeval:
            return 1
        elif not strRepr and not freeval:
            return 0
        else:
            print("Something wrong in getFree()")
            exit(1)


class Spectrum(SourceDescription):

    @staticmethod
    def getSpectrumObject(stype):

        if stype == "PowerLaw":
            return PowerLawSpectrum(stype)

        elif stype == "PLExpCutoff":
            return PLExpCutoffSpectrum(stype)

        elif stype == "PLSuperExpCutoff":
            return PLSuperExpCutoffSpectrum(stype)

        elif stype == "LogParabola":
            return LogParabolaSpectrum(stype)

        else:
            raise SpectrumTypeNotFoundError("Spectrum type '{}' is not supported. Supported spectrum types: ['PowerLaw', 'PLExpCutoff', 'PLSuperExpCutoff', 'LogParabola']".format(stype))


    def __init__(self, stype):
        self.stype = stype
        self.flux = Parameter("flux", "float", free = 0)

class PowerLawSpectrum(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.index = Parameter("index", "float", free=0, scale=-1.0, min=0.5, max=5)

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index}'

    def getParameterDict(self):
        return [self.index.toDict()]

class PLExpCutoffSpectrum(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.index = Parameter("index", "float", free=0, scale=-1.0, min=0.5, max=5)
        self.cutoffEnergy = Parameter("cutoffEnergy", "float", free=0, scale=-1.0, min=20, max=10000)

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index}\n{self.cutoffEnergy}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index.toDict(), self.cutoffEnergy.toDict()]

class PLSuperExpCutoffSpectrum(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.index1 = Parameter("index1", "float", free=0, scale=-1.0, min=0.5, max=5)
        self.cutoffEnergy = Parameter("cutoffEnergy", "float", free=0, scale=-1.0, min=20, max=10000)
        self.index2 = Parameter("index2", "float", free=0, scale=-1.0, min=0, max=100)

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index1}\n{self.cutoffEnergy}\n{self.index2}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index1.toDict(), self.cutoffEnergy.toDict(), self.index2.toDict()]

class LogParabolaSpectrum(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.flux = Parameter("flux", "float")
        self.index = Parameter("index", "float", free=0, scale=-1.0, min=1, max=4)
        self.pivotEnergy = Parameter("pivotEnergy", "float", free=0, scale=-1.0, min=500, max=3000)
        self.curvature = Parameter("curvature", "float", free=0, scale=-1.0, min=0.1, max=3)

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index}\n{self.pivotEnergy}\n{self.curvature}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index.toDict(), self.pivotEnergy.toDict(), self.curvature.toDict()]

class SpatialModel(SourceDescription):

    @staticmethod
    def getSpatialModelObject(type, ll):

        if type not in ["PointSource"]:

            raise WrongSpatialModelTypeError("SpatialModel type '%s' is not supported. Supported SpatialModel types: ['PointSource']".format(type))

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

        self.multiFlux = OutputVal("multiFlux", "float")
        self.multiFluxErr = OutputVal("multiFluxErr", "float")
        self.multiFluxPosErr = OutputVal("multiFluxPosErr", "float")
        self.multiFluxNegErr = OutputVal("multiFluxNegErr", "float")

        self.multiUL = OutputVal("multiUL", "float")

        self.multiErgLog = OutputVal("multiErgLog", "float")
        self.multiErgLogErr = OutputVal("multiErgLogErr", "float")


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

        self.multiGalCoeff = OutputVal("multiGalCoeff", "List<float>")
        self.multiGalErr = OutputVal("multiGalErr", "List<float>")

        self.multiIsoCoeff = OutputVal("multiIsoCoeff", "List<float>")
        self.multiIsoErr = OutputVal("multiIsoErr", "List<float>")

        self.startDataTT = OutputVal("startDataTT", "float")
        self.endDataTT = OutputVal("endDataTT", "float")


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

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.spatialModel = None
        self.spectrum = None
        self.multi = None


    def __str__(self):


        freeParams = [k for k,v in vars(self.spectrum).items() if isinstance(v, Parameter) and self.spectrum.getFree(k) > 0] + \
                        [k for k,v in vars(self.spatialModel).items() if isinstance(v, Parameter) and self.spatialModel.getFree(k) > 0]

        spectrumParams = [k+": "+v.get(strRepr=True) for k,v in vars(self.spectrum).items() if isinstance(v, Parameter)]

        strRepr = '\n-----------------------------------------------------------'
        strRepr += f'\nSource name: {self.name} ({self.type})'

        if self.multi:
            strRepr += " => sqrt(ts): "+str(self.multi.get("multiSqrtTS"))

        strRepr += f'\n  * Position:\n\t- start_pos: {self.spatialModel.get("pos")}'

        strRepr += f'\n  * Spectrum: ({self.spectrum.stype})'
        for sp in spectrumParams:
            strRepr += f'\n\t- {sp}'


        strRepr += f'\n  * Free params: '+' '.join(freeParams)

        if self.multi:
            strRepr += f'\n  * Multi analysis:'
            strRepr += f'\n\t- flux: {self.multi.get("multiFlux")} +- {self.multi.get("multiFluxErr")}'
            strRepr += f'\n\t- upper limit: {self.multi.get("multiUL")}'
            strRepr += f'\n\t- ergLog: {self.multi.get("multiErgLog")} +- {self.multi.get("multiErgLogErr")}'
            strRepr += f'\n\t- galCoeff: {self.multi.get("multiGalCoeff")}'
            strRepr += f'\n\t- isoCoeff: {self.multi.get("multiIsoCoeff")}'

            if "pos" in freeParams:
                strRepr += f'\n\t- L_peak: {self.multi.get("multiLPeak")}'
                strRepr += f'\n\t- B_peak: {self.multi.get("multiBPeak")}'
                strRepr += f'\n\t- distFromStartPos: {self.multi.get("multiDistFromStartPositionPeak")}'
                strRepr += f'\n\t- L: {self.multi.get("multiL")}'
                strRepr += f'\n\t- B: {self.multi.get("multiB")}'
                strRepr += f'\n\t- distFromStartPos: {self.multi.get("multiDistFromStartPosition")}'
                strRepr += f'\n\t- r: {self.multi.get("multir")}'
                strRepr += f'\n\t- a: {self.multi.get("multia")}'
                strRepr += f'\n\t- b: {self.multi.get("multib")}'
                strRepr += f'\n\t- phi: {self.multi.get("multiphi")}'


        """
        if self.spectrum:
            strRepr += f'{self.spectrum}'
        if self.spatialModel:
            strRepr += f'{self.spatialModel}'
        if self.multi:
            strRepr += f'{self.multi}'
        """

        strRepr += '\n-----------------------------------------------------------'
        return strRepr



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
            for k,v in Source.selectionParams["multi"].items():
                sparams += v
        else:
            for k,v in Source.selectionParams["source"].items():
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

    """
    self.label = Parameter("label", str)
    self.Fix = Parameter("Fix", int)
    self.index: float = None
    self.ULConfidenceLevel: float = None
    self.SrcLocConfLevel: float = None
    self.start_l: float = None
    self.start_b: float = None
    self.start_flux: float = None
    self.lmin: float = None
    self.lmax: float = None
    self.bmin: float = None
    self.bmax: float = None
    self.typefun: float = None
    self.par2: float = None
    self.par3: float = None
    self.galmode2: float = None
    self.galmode2fit: float = None
    self.isomode2: float = None
    self.isomode2fit: float = None
    self.edpcor: float = None
    self.fluxcor: float = None
    self.integratortype: float = None
    self.expratioEval: float = None
    self.expratio_minthr: float = None
    self.expratio_maxthr: float = None
    self.expratio_size: float = None
    self.index_min: float = None
    self.index_max: float = None
    self.par2_min: float = None
    self.par2_max: float = None
    self.par3_min: float = None
    self.par3_max: float = None
    self.contourpoints: float = None
    self.minimizertype: str = None
    self.minimizeralg: str = None
    self.minimizerdefstrategy: float = None
    self.minimizerdeftol: float = None

    self.SqrtTS: float = None

    self.L_peak: float = None
    self.B_peak: float = None
    self.Dist_from_start_position_peak: float = None

    self.L: float = None
    self.B: float = None
    self.Dist_from_start_position: float = None
    self.r: float = None
    self.a: float = None
    self.b: float = None
    self.phi: float = None

    self.Counts: float = None
    self.CountsErr: float = None
    self.CountsPosErr: float = None
    self.CountsNegErr: float = None
    self.CountsUL: float = None

    self.Flux: float = None
    self.FluxErr: float = None
    self.FluxPosErr: float = None
    self.FluxNegErr: float = None
    self.FluxUL: float = None
    self.FluxULbayes: float = None

    self.Exp: float = None
    self.ExpSpectraCorFactor: float = None

    self.Erg: float = None
    self.Erg_Err: float = None
    self.Erg_UL: float = None
    self.Erglog: float = None
    self.Erglog_Err: float = None
    self.Erglog_UL: float = None

    self.Sensitivity: float = None

    self.FluxPerChannel: List[float] = None

    self.Index: float = None
    self.Index_Err: float = None
    self.Par2: float = None
    self.Par2_Err: float = None
    self.Par3: float = None
    self.Par3_Err: float = None

    self.cts: float = None
    self.fitstatus0: float = None
    self.fcn0: float = None
    self.edm0: float = None
    self.nvpar0: float = None
    self.nparx0: float = None
    self.iter0: float = None
    self.fitstatus1: float = None
    self.fcn1: float = None
    self.edm1: float = None
    self.nvpar1: float = None
    self.nparx1: float = None
    self.iter1: float = None
    self.Likelihood1: float = None

    self.GalCoeff: List[float] = None
    self.GalErrs: List[float] = None

    self.GalZeroCoeff: List[float] = None
    self.GalZeroErrs: List[float] = None

    self.IsoCoeffs: List[float] = None
    self.IsoErrs: List[float] = None

    self.IsoZeroCoeffs: List[float] = None
    self.IsoZeroErrs: List[float] = None

    self.Start_date_UTC: datetime.datetime = None # 2018-06-03T12:01:07
    self.End_date_UTC: datetime.datetime = None   # 2018-06-04T00:01:07
    self.Start_data_TT: float = None
    self.End_data_TT: float = None
    self.Start_date_MJD: float = None
    self.End_date_MJD: float = None

    self.emin: float = List[float]
    self.emax: float = List[float]
    self.fovmin: float = List[float]
    self.fovmax: float = List[float]
    self.albedo: float = None
    self.binsize: float = None
    self.expstep: float = None
    self.phasecode: float = None
    self.ExpRatio: float = None

    self.ext1FitStatus: float = None
    self.step1FitStatus: float = None
    self.ext2FitStatus: float = None
    self.step2FitStatus: float = None
    self.contourFitStatus: float = None
    self.indexFitStatus: float = None
    self.ulFitStatus: float = None

    self.ext1Counts: float = None
    self.step1Counts: float = None
    self.ext2Counts: float = None
    self.step2Counts: float = None
    self.contourCounts: float = None
    self.indexCounts: float = None
    self.ulCounts: float = None

    self.SkytypeLFilterIrf: str = None
    self.SkytypeHFilterIrf: str = None

    self.Dist: float = None
    """
