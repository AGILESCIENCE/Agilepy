from abc import ABC, abstractmethod
from agilepy.core.source.SourceComponent import SourceComponent
from agilepy.core.CustomExceptions import SpectrumTypeNotFoundError, AttributeNotSupportedError

class Spectrum(ABC, SourceComponent):

    def __init__(self):
        pass
    
    @staticmethod
    def getSpectrum(spectrumType):

        if spectrumType == "PowerLaw":
            return PowerLaw()

        elif spectrumType == "PLExpCutoff":
            return PLExpCutoff()

        elif spectrumType == "PLSuperExpCutoff":
            return PLSuperExpCutoff()

        elif spectrumType == "LogParabola":
            return LogParabola()

        else:
            raise SpectrumTypeNotFoundError(f"Spectrum type '{spectrumType}' is not supported. Supported spectrum types: ['PowerLaw', 'PLExpCutoff', 'PLSuperExpCutoff', 'LogParabola']")

    def setParameter(self, parameterName, dictionaryValues):

        dictionaryKeys = list(dictionaryValues.keys())
        for key in dictionaryKeys:
            if key not in ["value", "err", "free", "min", "max"]:
                raise AttributeNotSupportedError(f"The attribute '{key}' is not supported for object of type '{type(spectrumObject)}'")

        parameter = getattr(self, parameterName)
        for key,val in dictionaryValues.items():
            parameter[key] = val 


    @abstractmethod 
    def getAttributes(self):
        pass


class PowerLaw(Spectrum):

    def __init__(self):
        self.flux =  {"name": "flux", "free": None, "value": None, "err": None, "datatype": "float"}
        self.index = {"name": "index", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}

    def getAttributes(self):
        return [self.flux, self.index]


class PLExpCutoff(Spectrum):

    def __init__(self):
        self.flux =  {"name": "flux", "free": None, "value": None, "err": None, "datatype": "float"}
        self.index = {"name": "index", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}
        self.cutoffEnergy = {"name": "cutoffEnergy", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}

    def getAttributes(self):
        return [self.flux, self.index, self.cutoffEnergy]


class PLSuperExpCutoff(Spectrum):

    def __init__(self):
        self.flux =  {"name": "flux", "free": None, "value": None, "err": None, "datatype": "float"}
        self.index1 = {"name": "index1", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}
        self.cutoffEnergy = {"name": "cutoffEnergy", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}
        self.index2 = {"name": "index2", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}

    def getAttributes(self):
        return [self.flux, self.index1, self.cutoffEnergy, self.index2]

class LogParabola(Spectrum):
    def __init__(self):
        self.flux = {"name": "flux", "free": None, "value": None, "err": None, "datatype": "float"}
        self.index = {"name": "index", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}
        self.pivotEnergy = {"name": "pivotEnergy", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}
        self.curvature = {"name": "curvature", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float"}

    def getAttributes(self):
        return [self.flux, self.index, self.pivotEnergy, self.curvature]

    