from dataclasses import dataclass, field
from typing import List
import datetime

class ValueParamFinder:

    def getParamAttributeWhere(self, attributeName, key, value):
        return [getattr(param, attributeName) for param in self.parameters if getattr(param, key) == value].pop()

    def searchParamAttribute(self, attributeName):
        for param in self.parameters:
            if getattr(param, "name") == attributeName:
                return param
        return None

    def setFreeAttributeValueOf(self, parameterName, freeval):
        for param in self.parameters:
            if getattr(param, "name") == parameterName:
                setattr(param, "free", freeval)

    def getFreeAttributeValueOf(self, key, value):
        try:
            return [getattr(param, "free") for param in self.parameters if getattr(param, key) == value].pop()
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

@dataclass
class SpatialModel(ValueParamFinder):
    type: str
    location_limit: int
    free: int
    parameters: List[Parameter]

    def __str__(self):
        return f'\n - SpatialModel type: {self.type} free: {self.free}'

@dataclass
class Spectrum(ValueParamFinder):
    type: str
    parameters: List[Parameter]
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
    minimizertype: float = None
    minimizeralg: str = None
    minimizerdefstrategy: str = None
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

    def __str__(self):
        return f'\n - MultiOutput  emin: {self.emin} emax: {self.emax} fovmin: {self.fovmin} fovmax: {self.fovmax} start_flux: {self.start_flux} sqrt(TS): {self.SqrtTS} multiDistanceFromMapCenter: {self.Dist}'


@dataclass(order=True)
class Source:
    name: str
    type: str
    multi: MultiOutput = None
    spatialModel: SpatialModel = None
    spectrum: Spectrum = None

    def __str__(self):
        repr = '----------------------------------------------------------------'
        repr += f'\nSource name: {self.name}\nSource type: {self.type}'
        if self.spectrum:
            repr += f'{self.spectrum}'
        if self.spatialModel:
            repr += f'{self.spatialModel}'
        if self.multi:
            repr += f'{self.multi}'
        repr += '\n----------------------------------------------------------------'
        return repr

    def setFreeAttributeValueOf(self, parameterName, free):

        if self.spatialModel.searchParamAttribute(parameterName):
            self.spatialModel.setFreeAttributeValueOf(parameterName, free)
            return True

        elif self.spectrum.searchParamAttribute(parameterName):
            self.spectrum.setFreeAttributeValueOf(parameterName, free)
            return True

        else:
            return False

    def __eq__(self, other):
        return self.name == other.name


"""
DONT NEED THIS CLASS
"""
@dataclass(eq=False)
class SourceLibrary:
    title: str
    sources: List[Source]

    def getSelectionParams(self, tostr = False, multi=False):
        sp = ["Dist", "Flux", "SqrtTS"]
        if not multi:
            sp.append("Name")
        if not tostr:
            return sp
        else:
            return ' '.join(sp)

    def getFreeParams(self, tostr = False):
        fp = ["Flux", "Index", "Index1", "Index2", "CutoffEnergy", "PivotEnergy", "Curvature", "Index2", "Loc"]
        if not tostr:
            return fp
        else:
            return ' '.join(fp)
