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
from agilepy.utils.CustomExceptions import WrongSpectrumTypeError, \
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
    def __init__(self, name, datatype=None):
        super().__init__(name, datatype)
        self.free = None
        self.scale = None
        self.min = None
        self.max = None
        self.location_limit = None

    def __str__(self):
        return f'\t- {self.name}: {self.value} free: {self.free}'

    def setFree(self, freeVal):
        if self.free == freeVal:
            return False
        else:
            self.free = freeVal
            return True

    def setAttributes(self, name=None, value=None, free=None, scale=None, min=None, max=None, location_limit=None):
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
        if location_limit is not None:
            self.location_limit = int(location_limit)

    def toDict(self):
        d = vars(self)
        outDict = {}
        for k,v in d.items():
            if v is not None and k!="datatype":
                outDict[k] = str(v)

        return outDict



class SourceDescription:

    def set(self, attributeName, attributeVal):
        getattr(self, attributeName).set(attributeVal)

    def get(self, attributeName, strRepr = False):
        return getattr(self, attributeName).get(strRepr) # calling Value's get()

    def setFree(self, attributeName, freeVal):
        return getattr(self, attributeName).setFree(freeVal)

    def getFree(self, attributeName, strRepr=False):
        freeval = getattr(self, attributeName).free
        if strRepr:
            freeval = str(freeval)
        return freeval


class Spectrum(SourceDescription):

    @staticmethod
    def getSpectrumObject(stype):

        if stype not in ["PowerLaw", "PLExpCutoff", "PLSuperExpCutoff", "LogParabola"]:

            raise WrongSpectrumTypeError("Spectrum type '%s' is not supported. Supported spectrum types: ['PowerLaw', 'PLExpCutoff', 'PLSuperExpCutoff', 'LogParabola']".format(stype))

        if stype == "PowerLaw":
            return PowerLawSpectrum(stype)

        elif stype == "PLExpCutoff":
            return PLExpCutoffSpectrum(stype)

        elif stype == "PLSuperExpCutoff":
            return PLSuperExpCutoffSpectrum(stype)

        else:
            return LogParabolaSpectrum(stype)

    def __init__(self, stype):
        self.stype = stype
        self.flux = Parameter("flux", "float")

class PowerLawSpectrum(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.index = Parameter("index", "float")

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index}'

    def getParameterDict(self):
        return [self.index.toDict()]

class PLExpCutoffSpectrum(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.flux = Parameter("flux", "float")
        self.index = Parameter("index", "float")
        self.cutoffEnergy = Parameter("cutoffEnergy", "float")

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index}\n{self.cutoffEnergy}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index.toDict(), self.cutoffEnergy.toDict()]

class PLSuperExpCutoffSpectrum(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.flux = Parameter("flux", "float")
        self.index1 = Parameter("index1", "float")
        self.cutoffEnergy = Parameter("cutoffEnergy", "float")
        self.index2 = Parameter("index2", "float")

    def __str__(self):
        return f'\n - Spectrum type: {self.stype}\n{self.flux}\n{self.index1}\n{self.cutoffEnergy}\n{self.index2}'

    def getParameterDict(self):
        return [self.flux.toDict(), self.index1.toDict(), self.cutoffEnergy.toDict(), self.index2.toDict()]

class LogParabolaSpectrum(Spectrum):
    def __init__(self, type):
        super().__init__(type)
        self.flux = Parameter("flux", "float")
        self.index = Parameter("index", "float")
        self.pivotEnergy = Parameter("pivotEnergy", "float")
        self.curvature = Parameter("curvature", "float")

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

        self.multiErg = OutputVal("multiErg", "float")
        self.multiErgErr = OutputVal("multiErgErr", "float")
        self.multiErgUL = OutputVal("multiErgUL", "float")

        self.multiL = OutputVal("multiL", "float")
        self.multiB = OutputVal("multiB", "float")
        self.multiStartL = OutputVal("multiStartL", "float")
        self.multiStartB = OutputVal("multiStartB", "float")

        self.multiDist = OutputVal("multiDist", "float")

    def __str__(self):
        return f'\n - SpatialModel\n{self.multiSqrtTS}\n{self.multiFlux}\n{self.multiFluxErr}\n{self.multiDist} \
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
        strRepr = '\n----------------------------------------------------------------'
        strRepr += f'\nSource name: {self.name}\nSource type: {self.type}'
        if self.spectrum:
            strRepr += f'{self.spectrum}'
        if self.spatialModel:
            strRepr += f'{self.spatialModel}'
        if self.multi:
            strRepr += f'{self.multi}'
        strRepr += '\n----------------------------------------------------------------'
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







































"""
class ValueParamFinder:

    def getParamAttributeWhere(self, attributeName, key, value, strRepr = False):
        val = [getattr(param, attributeName) for param in self.parameters if getattr(param, key) == value].pop()
        if strRepr:
            return str(val)
        else:
            return val

    def setParamValue(self, paramName, paramValue):
        for param in self.parameters:
            if getattr(param, "name") == paramName:
                setattr(param, "value", paramValue)
                return True
        return False

    def getParamValue(self, paramName):
        for param in self.parameters:
            if getattr(param, "name") == paramName:
                return getattr(param, "value")
        return None

    def getParam(self, paramName):
        for param in self.parameters:
            if getattr(param, "name") == paramName:
                return param
        return None



    def getFreeAttributeValueOf(self, key, value, strRepr = False):
        try:
            val = [getattr(param, "free") for param in self.parameters if getattr(param, key) == value].pop()
            if strRepr:
                return str(val)
            else:
                return val

        except Exception:
            return ""
"""













"""
@dataclass
class SpatialModel:

    type: str
    location_limit: int
    free: int
    dist: float
    parameters: List[Parameter]

    def __init__(self, type, location_limit, free):
        self.parameters = []
        self.type = type
        self.location_limit = float(location_limit)
        self.free = int(free)
        self.dist = None


    def __str__(self):
        return f'\n - SpatialModel type: {self.type} free: {self.free}\n\tglon: {self.parameters[0].value}\n\tglat: {self.parameters[1].value}\n\tdist: {self.dist}'

"""


"""
@dataclass
class Parameter:

    name: str
    value: float
    free: bool = None
    scale: float = None
    min: float = None
    max: float = None

    def __init__(self, name, value, free=None, scale=None, min=None, max=None):

        self.name = name
        self.value = float(value)
        if free is not None:
            self.free = int(free)
        if scale is not None:
            self.scale = float(scale)
        if min is not None:
            self.min = float(min)
        if max is not None:
            self.max = float(max)

    def toDict(self):
        d = vars(self)
        for k,v in d.items():
            d[k] = str(v)
        return d
"""
"""

@dataclass
class SpatialModel(ValueParamFinder):
    type: str
    location_limit: int
    free: int
    dist: float
    parameters: List[Parameter]

    def __init__(self, type, location_limit, free):
        self.parameters = []
        self.type = type
        self.location_limit = float(location_limit)
        self.free = int(free)
        self.dist = None


    def __str__(self):
        return f'\n - SpatialModel type: {self.type} free: {self.free}\n\tglon: {self.parameters[0].value}\n\tglat: {self.parameters[1].value}\n\tdist: {self.dist}'
@dataclass
class Spectrum(ValueParamFinder):
    type: str
    parameters: List[Parameter]
    def __init__(self, type):
        self.type = type
        self.parameters = []

    def __str__(self):
        paramsStr = ""
        for p in self.parameters:
            paramsStr += f'\n\t{p.name}={p.value} free={p.free}'
        return f'\n - Spectrum type: {self.type} {paramsStr}'
"""
"""
@dataclass
class MultiOutput:


    label: str  = None #  == Source.name ?
    Fix: int  = None
    index: float = None
    ULConfidenceLevel: float = None
    SrcLocConfLevel: float = None
    start_l: float = None
    start_b: float = None
    start_flux: float = None
    lmin: float = None
    lmax: float = None
    bmin: float = None
    bmax: float = None
    typefun: float = None
    par2: float = None
    par3: float = None
    galmode2: float = None
    galmode2fit: float = None
    isomode2: float = None
    isomode2fit: float = None
    edpcor: float = None
    fluxcor: float = None
    integratortype: float = None
    expratioEval: float = None
    expratio_minthr: float = None
    expratio_maxthr: float = None
    expratio_size: float = None
    index_min: float = None
    index_max: float = None
    par2_min: float = None
    par2_max: float = None
    par3_min: float = None
    par3_max: float = None
    contourpoints: float = None
    minimizertype: str = None
    minimizeralg: str = None
    minimizerdefstrategy: float = None
    minimizerdeftol: float = None

    SqrtTS: float = None

    L_peak: float = None
    B_peak: float = None
    Dist_from_start_position_peak: float = None

    L: float = None
    B: float = None
    Dist_from_start_position: float = None
    r: float = None
    a: float = None
    b: float = None
    phi: float = None

    Counts: float = None
    CountsErr: float = None
    CountsPosErr: float = None
    CountsNegErr: float = None
    CountsUL: float = None

    Flux: float = None
    FluxErr: float = None
    FluxPosErr: float = None
    FluxNegErr: float = None
    FluxUL: float = None
    FluxULbayes: float = None

    Exp: float = None
    ExpSpectraCorFactor: float = None

    Erg: float = None
    Erg_Err: float = None
    Erg_UL: float = None
    Erglog: float = None
    Erglog_Err: float = None
    Erglog_UL: float = None

    Sensitivity: float = None

    FluxPerChannel: List[float] = None

    Index: float = None
    Index_Err: float = None
    Par2: float = None
    Par2_Err: float = None
    Par3: float = None
    Par3_Err: float = None

    cts: float = None
    fitstatus0: float = None
    fcn0: float = None
    edm0: float = None
    nvpar0: float = None
    nparx0: float = None
    iter0: float = None
    fitstatus1: float = None
    fcn1: float = None
    edm1: float = None
    nvpar1: float = None
    nparx1: float = None
    iter1: float = None
    Likelihood1: float = None

    GalCoeff: List[float] = None
    GalErrs: List[float] = None

    GalZeroCoeff: List[float] = None
    GalZeroErrs: List[float] = None

    IsoCoeffs: List[float] = None
    IsoErrs: List[float] = None

    IsoZeroCoeffs: List[float] = None
    IsoZeroErrs: List[float] = None

    Start_date_UTC: datetime.datetime = None # 2018-06-03T12:01:07
    End_date_UTC: datetime.datetime = None   # 2018-06-04T00:01:07
    Start_data_TT: float = None
    End_data_TT: float = None
    Start_date_MJD: float = None
    End_date_MJD: float = None

    emin: float = List[float]
    emax: float = List[float]
    fovmin: float = List[float]
    fovmax: float = List[float]
    albedo: float = None
    binsize: float = None
    expstep: float = None
    phasecode: float = None
    ExpRatio: float = None

    ext1FitStatus: float = None
    step1FitStatus: float = None
    ext2FitStatus: float = None
    step2FitStatus: float = None
    contourFitStatus: float = None
    indexFitStatus: float = None
    ulFitStatus: float = None

    ext1Counts: float = None
    step1Counts: float = None
    ext2Counts: float = None
    step2Counts: float = None
    contourCounts: float = None
    indexCounts: float = None
    ulCounts: float = None

    SkytypeLFilterIrf: str = None
    SkytypeHFilterIrf: str = None

    Dist: float = None

    def convertToFloat(self):

        # filtering out methods
        attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))

        # filtering out special names
        attributes = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]

        for a in attributes:

            attrName = a[0]
            attrVal = a[1]

            if attrName in ["FluxPerChannel", "GalCoeff", "GalErrs", "GalZeroCoeff", "GalZeroErrs", "IsoCoeffs", "IsoErrs", "IsoZeroCoeffs", "IsoZeroErrs", "emin", "emax", "fovmin", "fovmax"]:
                listelem = getattr(self, attrName)
                newl = [float(elem) for elem in listelem]
                setattr(self, attrName, newl)

            elif attrName in ["label", "minimizeralg", "minimizertype", "Start_date_UTC", "End_date_UTC", "SkytypeLFilterIrf", "SkytypeHFilterIrf"]:
                pass

            else:
                attrVal = getattr(self, attrName)

                if attrVal:
                    setattr(self, attrName, float(attrVal))

    def __str__(self):

        return f'\n - MultiOutput\n\tstart_flux: {self.start_flux}\n\tFlux: {self.Flux}\n\tDist: {self.Dist}\n\tsqrt(TS): {self.SqrtTS}'


"""
"""
@dataclass(order=True)
class Source:
    name: str
    type: str
    multi: MultiOutput = None
    spatialModel: SpatialModel = None
    spectrum: Spectrum = None

    def __str__(self):
        strRepr = '----------------------------------------------------------------'
        strRepr += f'\nSource name: {self.name}\nSource type: {self.type}'
        if self.spectrum:
            strRepr += f'{self.spectrum}'
        if self.spatialModel:
            strRepr += f'{self.spatialModel}'
        if self.multi:
            strRepr += f'{self.multi}'
        strRepr += '\n----------------------------------------------------------------'
        return strRepr

    def from_dict(self, name, source_dict):

        errors = []
        fail = False

        if "name" not in source_dict:
            errors.append("The input dictinary does not contain the requried 'name' key")
            fail = True
        else:
            sourceDC = Source(source_dict["name"], "PointSource")

        if "spectrum" not in source_dict:
            errors.append("The input dictinary does not contain the requried 'spectrum' key")
            fail = True
        else:
            spectrum = Spectrum(source_dict["spectrum"]["type"])
            # sourceDescrDC = SourcesLibrary._checkAndAddParameters(sourceDescrDC, sourceDescription)
            sourceDC.spectrum = spectrum

        if "spatialModel" not in source_dict:
            errors.append("The input dictinary does not contain the requried 'spatialModel' key")
            fail = True
        else:
            spatialModel = SpatialModel(source_dict["spatialModel"]["type"], source_dict["spatialModel"]["location_limit"], source_dict["spatialModel"]["free"])
            # sourceDescrDC = SourcesLibrary._checkAndAddParameters(sourceDescrDC, sourceDescription)
            sourceDC.spatialModel = spatialModel


        return sourceDC

    def getSelectionValue(self, paramName):

        if paramName == "Name" or paramName == "name":
            return self.name

        elif paramName == "Flux" or paramName == "flux":
            if self.multi:
                return self.multi.Flux
            else:
                return self.spectrum.getParamValue("Flux")

        elif paramName == "Dist" or paramName == "dist":
            if self.multi:
                return self.multi.Dist
            else:
                return self.spatialModel.dist

        elif paramName == "SqrtTS" or paramName == "sqrtTS":

            return self.multi.SqrtTS

        else:

            return None


    def setParamValue(self, key, val):

        if key in ["Flux", "Index", "Index1", "Index2", "CutoffEnergy", "PivotEnergy", "Curvature"] :
            return self.spectrum.setParamValue(key, val)

        elif key in ["GLON", "GLAT"]:
            return self.spatialModel.setParamValue(key, val)

        else:
            return False


    def getParamValue(self, key):

        if key in ["Flux", "Index", "Index1", "Index2", "CutoffEnergy", "PivotEnergy", "Curvature"] :
            return self.spectrum.getParamValue(key)

        elif key in ["GLON", "GLAT"]:
            return self.spatialModel.getParamValue(key)

        else:
            return False


    def setFreeAttributeValueOf(self, parameterName, free):

        if self.spatialModel.getParam(parameterName):
            self.spatialModel.setFreeAttributeValueOf(parameterName, free)
            return True

        elif self.spectrum.getParam(parameterName):
            self.spectrum.setFreeAttributeValueOf(parameterName, free)
            return True

        else:
            return False

    def __eq__(self, other):
        return self.name == other.name
"""
