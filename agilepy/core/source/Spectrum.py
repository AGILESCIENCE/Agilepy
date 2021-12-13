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
            if key not in ["name", "value", "err", "free", "min", "max", "scale"]:
                raise AttributeNotSupportedError(f"The attribute '{key}' is not supported for object of type '{type(self)}'")

        parameter = getattr(self, parameterName)
        for key,val in dictionaryValues.items():
            try: parameter[key] = eval(val)       
            except: parameter[key] = val
        
        return True

    @abstractmethod 
    def getAttributes(self):
        pass
    
    @abstractmethod
    def getSpectralIndex(self):
        pass



class PowerLaw(Spectrum):

    def __init__(self):
        self.flux =  {"name": "flux", "free": None, "value": None, "err": None, "datatype": "float", "um" : "ph/cm2s"}
        self.index = {"name": "index", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}

    def getAttributes(self):
        return [self.flux, self.index]

    def getSpectralIndex(self):
        return self.index["value"]

class PLExpCutoff(Spectrum):

    def __init__(self):
        self.flux =  {"name": "flux", "free": None, "value": None, "err": None, "datatype": "float", "um" : "ph/cm2s"}
        self.index = {"name": "index", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}
        self.cutoffEnergy = {"name": "cutoffEnergy", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}

    def getAttributes(self):
        return [self.flux, self.index, self.cutoffEnergy]

    def getSpectralIndex(self):
        return self.index["value"]

class PLSuperExpCutoff(Spectrum):

    def __init__(self):
        self.flux =  {"name": "flux", "free": None, "value": None, "err": None, "datatype": "float", "um" : "ph/cm2s"}
        self.index1 = {"name": "index1", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}
        self.cutoffEnergy = {"name": "cutoffEnergy", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}
        self.index2 = {"name": "index2", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}

    def getAttributes(self):
        return [self.flux, self.index1, self.cutoffEnergy, self.index2]

    def getSpectralIndex(self):
        return self.index1["value"]

class LogParabola(Spectrum):
    def __init__(self):
        self.flux = {"name": "flux", "free": None, "value": None, "err": None, "datatype": "float", "um" : "ph/cm2s"}
        self.index = {"name": "index", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}
        self.pivotEnergy = {"name": "pivotEnergy", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}
        self.curvature = {"name": "curvature", "value": None, "err": None, "free": None, "min": None, "max": None, "scale": None, "datatype": "float", "um" : ""}

    def getAttributes(self):
        return [self.flux, self.index, self.pivotEnergy, self.curvature]

    def getSpectralIndex(self):
        return self.index["value"]