from agilepy.core.CustomExceptions import AttributeNotSupportedError
from agilepy.core.source.SourceComponent import SourceComponent

class SpatialModel(SourceComponent):

    def __init__(self):
        pass
    
    @staticmethod
    def getSpatialModel(spatialModelType):

        if spatialModelType == "PointSource":
            return PointSource() 

    def setParameter(self, parameterName, dictionaryValues):

        dictionaryKeys = list(dictionaryValues.keys())
        for key in dictionaryKeys:
            if key not in ["value", "free"]:
                raise AttributeNotSupportedError(f"The attribute '{key}' is not supported for object of type '{type(spectrumObject)}'")

        parameter = getattr(self, parameterName)
        for key,val in dictionaryValues.items():
            parameter[key] = val 
    

class PointSource(SpatialModel):

    def __init__(self):
        self.pos =  {"name": "pos", "free": None, "value": None, "datatype": "float"}
        self.dist =  {"name": "dist", "value": None, "datatype": "float"}
        self.locationLimit =  {"name": "locationLimit", "value": None, "datatype": "int"}
    
    def __str__(self):
        return f'\n - SpatialModel type: {type(self)}\n{self.pos["value"]}\n{self.dist["value"]}\n{self.locationLimit["value"]}'
