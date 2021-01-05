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

from pathlib import Path
from typing import List
from numbers import Number

from agilepy.utils.Utils import Utils
from agilepy.utils.CustomExceptions import ConfigFileOptionTypeError

class ValidationStrategies:
    
    @staticmethod
    def _validateEvtFile(confDict):

        errors = {}
        
        if not Path(confDict["input"]["evtfile"]).exists():
            error_str = f"The evtfile={confDict['input']['evtfile']} does not exist."
            errors["input/evtfile"] = error_str            
        
        return errors

    @staticmethod
    def _validateLogFile(confDict):
        
        errors = {}

        if not Path(confDict["input"]["logfile"]).exists():
            error_str = f"The logfile={confDict['input']['logfile']} does not exist."
            errors["input/logfile"] = error_str            
        
        return errors

    @staticmethod
    def _validateBackgroundCoeff(confDict):

        errors = {}

        numberOfEnergyBins = len(confDict["maps"]["energybins"])
        fovbinnumber = confDict["maps"]["fovbinnumber"]

        numberOfMaps = numberOfEnergyBins*fovbinnumber

        isocoeff = confDict["model"]["isocoeff"]
        galcoeff = confDict["model"]["galcoeff"]

        numberOfIsoCoeff = len(isocoeff)

        if numberOfIsoCoeff < numberOfMaps:

            error_str = f"The number of bg isotropic coefficients {isocoeff} is less then the number of numberOfMaps {numberOfMaps} (number of maps = number of energy bins*fovbinnumber)"

            errors["model/isocoeff"] = error_str

        numberOfGalCoeff = len(galcoeff)

        if numberOfGalCoeff < numberOfMaps:

            error_str = f"The number of bg galactic coefficients {galcoeff} is less then the number of numberOfMaps {numberOfMaps} (number of maps = number of energy bins*fovbinnumber)"

            errors["model/galcoeff"] = error_str

        return errors

    @staticmethod
    def _validateIndexFiles(confDict):

        errors = {}

        pathEvt = Path(confDict["input"]["evtfile"])

        if not pathEvt.exists() or not pathEvt.is_file():
            errors["input/evtfile"]="File {} not exists".format(confDict["input"]["evtfile"])

        pathLog = Path(confDict["input"]["logfile"])

        if not pathLog.exists() or not pathLog.is_file():
            errors["input/logfile"]="File {} not exists".format(confDict["input"]["logfile"])

        return errors

    @staticmethod
    def _validateTimeInIndex(confDict):
        errors = {}

        (first, last) = Utils._getFirstAndLastLineInFile(confDict["input"]["evtfile"])

        idxTmin = Utils._extractTimes(first)[0]
        idxTmax = Utils._extractTimes(last)[1]

        userTmin = confDict["selection"]["tmin"]
        userTmax = confDict["selection"]["tmax"]



        if float(userTmin) < float(idxTmin):
            errors["input/tmin"]="tmin: {} is outside the time range of {} (tmin < indexTmin). Index file time range: [{}, {}]" \
                                  .format(confDict["selection"]["tmin"], confDict["input"]["evtfile"], idxTmin, idxTmax)

        if float(userTmin) > float(idxTmax):
            errors["input/tmin"]="tmin: {} is outside the time range of {} (tmin > indexTmax). Index file time range: [{}, {}]" \
                                  .format(confDict["selection"]["tmin"], confDict["input"]["evtfile"], idxTmin, idxTmax)


        if float(userTmax) > float(idxTmax):
            errors["input/tmax"]="tmax: {} is outside the time range of {} (tmax > indexTmax). Index file time range: [{}, {}]" \
                                  .format(confDict["selection"]["tmax"], confDict["input"]["evtfile"], idxTmin, idxTmax)

        if float(userTmax) < float(idxTmin):
            errors["input/tmax"]="tmax: {} is outside the time range of {} (tmax < indexTmin). Index file time range: [{}, {}]" \
                                  .format(confDict["selection"]["tmax"], confDict["input"]["evtfile"], idxTmin, idxTmax)

        return errors

    @staticmethod
    def _validateTimetype(confDict):

        errors = {}

        if confDict["selection"]["timetype"] not in ["TT", "MJD"]:

            errors["selection/timetype"] = f"timetype value {confDict['selection']['timetype']} not supported. Supported values: 'TT', 'MJD' "

        return errors

    @staticmethod
    def _validateMinMax(confDict, section, optionMin, optionMax):

        errors = {}

        if confDict[section][optionMin] > confDict[section][optionMax]:

            errors[section+"/"+optionMin] = "%s cannot be greater than %s" % (optionMin, optionMax)

        if confDict[section][optionMin] == confDict[section][optionMax]:

            errors[section+"/"+optionMin] = "%s cannot be equal to %s" % (optionMin, optionMax)

        return errors

    @staticmethod
    def _validateLOCCL(confDict):

        errors = {}

        loccl = confDict["mle"]["loccl"]

        if loccl not in [9.21034, 5.99147, 2.29575, 1.38629]:

            errors["mle/loccl"] = "loccl values ({}) is not compatibile.. Possible values = [9.21034, 5.99147, 2.29575, 1.38629]".format(loccl)

        return errors


    @staticmethod
    def _validateOptionType(optionName, optionValue, validType):

        # validType  (type, dimensione)
        # optionValue possible values: 1  3.4   [1]  [4.5]  [[1,1], [1,2]]  [[1.0,1.1], [1.3,2.4]]   "ciao"   ["ciao"]   [["ciao","ciao"], ["ciao", "ciao"]]

        # verify the data dimension

        # if scalar
        if not isinstance(optionValue, List):

            if validType[1] != 0:
                raise ConfigFileOptionTypeError("Can't set config option '{}'. Error: expected dimension=scalar {} but you passed dimension={}".format(optionName, validType[1], type(optionValue)))
            
            # int is a Number...
            if (type(optionValue)==int or type(optionValue)==float) and validType[0]==Number:
                pass
            
            elif type(optionValue) != validType[0]:
                raise ConfigFileOptionTypeError("Can't set config option '{}'. Error: expected type={} but you passed {} of type={}".format(optionName, validType[0], optionValue, type(optionValue)))



        # if array1D
        elif isinstance(optionValue, List) and not isinstance(optionValue[0], List):

            if validType[1] != 1:
                raise ConfigFileOptionTypeError("Can't set config option '{}'. Error: expected dimension=Array1d (List) but you passed dimension={}".format(optionName, type(optionValue)))

            for i, elem in enumerate(optionValue):

                # int is a Number...
                if (type(elem)==int or type(elem)==float) and validType[0]==Number:
                    pass

                elif type(elem) != validType[0]:
                    raise ConfigFileOptionTypeError("Can't set config option '{}'. Error: expected type={} but you passed {}. Elem of index {} ({}) has the type={}".format(optionName, validType[0], optionValue, i, elem, type(elem)))



        # if array2D
        elif isinstance(optionValue, List) and isinstance(optionValue[0], List):

            if validType[1] != 2:
                raise ConfigFileOptionTypeError("Can't set config option '{}'. Error: expected dimension=Array2d (List<List>) but you passed dimension={}".format(optionName, type(optionValue)))

            for i, arr in enumerate(optionValue):
                for j, elem in enumerate(arr): 
                
                    # int is a Number...
                    if (type(elem)==int or type(elem)==float) and validType[0]==Number:
                        pass

                    elif type(elem) != validType[0]:
                        raise ConfigFileOptionTypeError("Can't set config option '{}'. Error: expected type={} but you passed {}. Elem of index {},{} ({}) has the type={}".format(optionName, validType[0], optionValue, i, j, elem, type(elem)))
