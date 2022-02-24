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
            if key not in ["name", "value", "free"]:
                raise AttributeNotSupportedError(f"The attribute '{key}' is not supported for object of type '{type(self)}'")

        parameter = getattr(self, parameterName)
        for key,val in dictionaryValues.items():
            try: parameter[key] = eval(val)       
            except: parameter[key] = val
    

class PointSource(SpatialModel):

    def __init__(self):
        self.pos =  {"name": "pos", "free": False, "value": None, "datatype": "Tuple<float,float>", "um": "(l,b)"}
        self.dist =  {"name": "dist", "value": None, "datatype": "float", "um": "deg"}
        self.locationLimit =  {"name": "locationLimit", "value": None, "datatype": "int", "um": ""}
    
    def __str__(self):
        return f'\n - SpatialModel type: {type(self)}\n{self.pos["value"]}\n{self.dist["value"]}\n{self.locationLimit["value"]}'

    def getAttributes(self):
        return [self.pos, self.dist, self.locationLimit]
