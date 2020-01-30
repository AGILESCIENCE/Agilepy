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

    def setFreeAttributeValueOf(self, parameterName, freeval):
        for param in self.parameters:
            if getattr(param, "name") == parameterName:
                setattr(param, "free", freeval)

    def getFreeAttributeValueOf(self, key, value, strRepr = False):
        try:
            val = [getattr(param, "free") for param in self.parameters if getattr(param, key) == value].pop()
            if strRepr:
                return str(val)
            else:
                return val

        except Exception:
            return ""

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


@dataclass
class SpatialModel(ValueParamFinder):
    type: str
    location_limit: int
    free: int
    parameters: List[Parameter]

    def __init__(self, type, location_limit, free):
        self.parameters = []
        self.type = type
        self.location_limit = float(location_limit)
        self.free = int(free)


    def __str__(self):
        return f'\n - SpatialModel type: {self.type} free: {self.free} glon: {self.parameters[0].value} glat: {self.parameters[1].value}'

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
            paramsStr += f'\n      {p.name}={p.value} free={p.free}'
        return f'\n - Spectrum type: {self.type} {paramsStr}'

@dataclass
class MultiOutput:
    """

        !! DO NOT CHANGE THE ORDER OF THESE ATTRIBUTES !!

    """
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


        return f'\n - MultiOutput  Flux: {self.Flux} Dist: {self.Dist} emin: {self.emin} emax: {self.emax} fovmin: {self.fovmin} \
                      fovmax: {self.fovmax} start_flux: {self.start_flux} sqrt(TS): {self.SqrtTS} \
                      multiDistanceFromMapCenter: {self.Dist}'




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
