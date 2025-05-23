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
import numpy as np
from numbers import Number
from agilepy.core.Parameters import Parameters

from agilepy.utils.Utils import Utils
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.CustomExceptions import ConfigFileOptionTypeError, DeprecatedOptionError

class ValidationStrategies:
    """
    @staticmethod
    def _validateEvtFile(confDict): #DEPRECATED

        errors = {}

        if confDict["input"]["userestapi"] and (len(listdir(Path(confDict["input"]["datapath"]))) == 0):
           return errors

        if Path(confDict["input"]["evtfile"]) is None and confDict["input"]["userestapi"] == False:
            error_str = f"evtfile is None and userestapi is set to False"
            errors["input/evtfile"] = error_str
        
        elif not Path(confDict["input"]["evtfile"]).exists():
            error_str = f"The evtfile={confDict['input']['evtfile']} does not exist."
            errors["input/evtfile"] = error_str            
        
        return errors

    @staticmethod
    def _validateLogFile(confDict): DEPRECATED
        
        errors = {}

        if confDict["input"]["userestapi"] and (len(listdir(Path(confDict["input"]["datapath"]))) == 0):
           return errors

        if Path(confDict["input"]["logfile"]) is None and confDict["input"]["userestapi"] == False:
            error_str = f"logfile is None and userestapi is set to False"
            errors["input/logfile"] = error_str

        elif not Path(confDict["input"]["logfile"]).exists():
            error_str = f"The logfile={confDict['input']['logfile']} does not exist."
            errors["input/logfile"] = error_str            
        
        return errors
    """


    @staticmethod
    def _validateVerboseLvl(confDict):

        errors = {}

        if confDict["output"]["verboselvl"] not in [0, 1, 2, 3]:

            errors["output/verboselvl"] = f"Invalid value for verboselvl={confDict['output']['verboselvl']}. Allowed values are 0 (ERROR), 1 (WARNING), 2 (INFO), 3 (DEBUG)"

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

            error_str = f"The number of isotropic coefficients (galcoeff={isocoeff}) must be equal to X = number of energy bins * fovbinnumber)"

            errors["model/isocoeff"] = error_str

        numberOfGalCoeff = len(galcoeff)

        if numberOfGalCoeff < numberOfMaps:

            error_str = f"The number of galcoeff coefficients (galcoeff={galcoeff}) must be equal to X = number of energy bins * fovbinnumber)"

            errors["model/galcoeff"] = error_str

        return errors

    @staticmethod
    def _validateIndexFiles(confDict):

        errors = {}

        #print(f"{type(confDict['input']['userestapi'])} \n\n\n\n {len(listdir(Path(confDict['input']['datapath'])))}")
        if confDict["input"]["userestapi"]:
            return errors

        pathEvt = Path(confDict["input"]["evtfile"])

        if not pathEvt.exists() or not pathEvt.is_file():
            errors["input/evtfile"]="File {} not exists".format(confDict["input"]["evtfile"])

        pathLog = Path(confDict["input"]["logfile"])

        if not pathLog.exists() or not pathLog.is_file():
            errors["input/logfile"]="File {} not exists".format(confDict["input"]["logfile"])

        return errors


    #Deprecated after 1.5.0 release
    @staticmethod
    def _validateTimeInIndex(confDict):
        errors = {}

        if (confDict["input"]["userestapi"] == True):
            return errors

        (first, last) = Utils._getFirstAndLastLineInFile(confDict["input"]["evtfile"])

        idxTmin = Utils._extractTimes(first)[0]
        idxTmax = Utils._extractTimes(last)[1]

        userTmin = confDict["selection"]["tmin"]
        userTmax = confDict["selection"]["tmax"]
        timetype = confDict["selection"]["timetype"]

        if timetype == "MJD":
            userTmin = AstroUtils.time_mjd_to_agile_seconds(userTmin)
            userTmax = AstroUtils.time_mjd_to_agile_seconds(userTmax)

        if float(userTmin) < float(idxTmin):
            errors["input/tmin"]="tmin: {} is outside the time range of {} (tmin < indexTmin). Index file time range: [{}, {}]" \
                                  .format(userTmin, confDict["input"]["evtfile"], idxTmin, idxTmax)

        if float(userTmin) > float(idxTmax):
            errors["input/tmin"]="tmin: {} is outside the time range of {} (tmin > indexTmax). Index file time range: [{}, {}]" \
                                  .format(userTmin, confDict["input"]["evtfile"], idxTmin, idxTmax)


        if float(userTmax) > float(idxTmax):
            errors["input/tmax"]="tmax: {} is outside the time range of {} (tmax > indexTmax). Index file time range: [{}, {}]" \
                                  .format(userTmax, confDict["input"]["evtfile"], idxTmin, idxTmax)

        if float(userTmax) < float(idxTmin):
            errors["input/tmax"]="tmax: {} is outside the time range of {} (tmax < indexTmin). Index file time range: [{}, {}]" \
                                  .format(userTmax, confDict["input"]["evtfile"], idxTmin, idxTmax)

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

        if loccl not in [9.21034, 5.99147, 2.29575, 1.38629, 0]:

            errors["mle/loccl"] = "loccl values ({}) is not compatibile.. Possible values = [9.21034, 5.99147, 2.29575, 1.38629, 0.0]".format(loccl)

        return errors
    
    @staticmethod
    def _validateFluxcorrection(confdict):
        
        errors = {}

        fluxcorrection = confdict["mle"]["fluxcorrection"]

        if fluxcorrection not in [0, 1, 2]:
            errors["mle/fluxcorrection"] = "fluxcorrection is not compatible.. Possible values = [1, 2, 3]"
        
        return errors

    @staticmethod
    def _validateDQ(confdict):
        
        errors = {}
        
        dq = confdict["selection"]["dq"]

        if dq < 0 or dq > 9:
            errors["selection/dq"] = f"dq = {confdict['selection']['dq']} -> invalid value. Possible values [0,1,2,3,4,5,6,7,8,9]"
        
        return errors


    """@staticmethod
    def _validateAlbedorad(confdict):
        
        errors = {}

        dq = confdict["selection"]["dq"]

        if dq != 0:
            errors["selection/albedorad"] = f"dq = {confdict['selection']['dq']} -> you can't change albedorad (nor fovradmax). Set dq to 0 if you want to use custom values for albedorad or fovradmax"
        
        return errors
    
    @staticmethod
    def _validateFovradmax(confDict):
        
        errors = {}
        
        dq = confDict["selection"]["dq"]
        if dq != 0:
             errors["selection/fovradmax"] = f"dq = {confDict['selection']['dq']} -> you can't change fovradmax (nor albedorad). Set dq to 0 if you want to use custom values for albedorad or fovradmax"

        return errors"""

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
            if (type(optionValue) in [int, float, np.int64, np.float64]) and validType[0]==Number:
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
    @staticmethod
    def _validateDatapath(confDict):
        
        errors = {}
        
        if Path(confDict["input"]["datapath"]) is None and confDict["input"]["userestapi"] == True:
            error_str = f"datapath is None and userestapi is set to True"
            errors["input/datapath"] = error_str

        return errors
    

    @staticmethod
    def _validateIrf(confDict, section, option):
        
        errors = {}
        
        if confDict[section][option] is None:
            errors["selection/irf"] = "irf is None"

        if confDict[section][option] not in Parameters.getSupportedIRFs():
            errors["selection/irf"] = f"irf = {confDict[section][option]} -> invalid value. Possible values {Parameters.getSupportedIRFs()}" 

        return errors    


    @staticmethod
    def _validateDeprecatedOptions(confDict, removed_options=None, parent_key=''):
        """Check if an option of the configuration is in a list of removed options.

        Args:
            confDict (dict): Configuration Dictionary.
            removed_options (list, optional): List of removed options. Defaults to None.
            parent_key (str, optional): _description_. Defaults to ''.

        Raises:
            DeprecatedOptionError (agilepy.core.CustomException.DeprecatedOptionError): Option was deprecated and is now removed.
        """
        errors = {}
        
        # List the deprecated options, now removed
        if removed_options is None:
            removed_options = ['emin', 'emax', 'min', 'max']

        for key, value in confDict.items():
            full_key = f"{parent_key}/{key}" if parent_key else key

            if key in removed_options:
                errors[full_key]=f"The configuration option \'{full_key}\' has been removed and is no longer supported."
                #raise DeprecatedOptionError(f"The configuration option \'{full_key}\' has been removed and is no longer supported.")

            # Call recursively for nested keys
            if isinstance(value, dict):
                errors.update(ValidationStrategies._validateDeprecatedOptions(value, removed_options, full_key))
                
        return errors

