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

import os
import yaml
import pprint
import numbers
from typing import List
from copy import deepcopy
from numbers import Number
from os.path import dirname, realpath, join, expandvars
from pathlib import Path

from agilepy.utils.AstroUtils import AstroUtils
from agilepy.utils.CustomExceptions import ConfigurationsNotValidError, \
                                           OptionNotFoundInConfigFileError, \
                                           ConfigFileOptionTypeError, \
                                           CannotSetHiddenOptionError, \
                                           CannotSetNotUpdatableOptionError



class AgilepyConfig():
    """

    """
    def __init__(self):

        self.pp = pprint.PrettyPrinter(indent=2)
        self.initialized = False
        self.conf = None

    @staticmethod
    def getCopy(copyFrom):
        ac = AgilepyConfig()
        ac.conf = deepcopy(copyFrom.conf)
        ac.initialized = True
        return ac

    def loadConfigurations(self, configurationFilePath, validate = True):

        currentDir = dirname(realpath(__file__))

        default_conf = AgilepyConfig._loadFromYaml(join(currentDir,"./conf.default.yaml"))

        user_conf = AgilepyConfig._loadFromYaml(configurationFilePath)

        mergedConf = AgilepyConfig._mergeConfigurations(default_conf, user_conf)

        AgilepyConfig._checkRequiredParams(mergedConf)

        conf = AgilepyConfig._completeConfiguration(mergedConf)

        self.conf = conf
        # self.conf_bkp = deepcopy(self.conf)

        if validate:

            self.validateConfiguration()

        self.initialized = True

    def validateConfiguration(self):

        errors = {}

        errors.update( AgilepyConfig._validateBackgroundCoeff(self.conf) )
        errors.update( AgilepyConfig._validateIndexFiles(self.conf) )
        errors.update( AgilepyConfig._validateTimeInIndex(self.conf) )
        errors.update( AgilepyConfig._validateLOCCL(self.conf) )
        errors.update( AgilepyConfig._validateMinMax(self.conf, "selection", "fovradmin", "fovradmax") )
        errors.update( AgilepyConfig._validateMinMax(self.conf, "selection", "emin", "emax") )

        if errors:
            raise ConfigurationsNotValidError("Errors: {}".format(errors))

    # def getCopy(self):



    #@ deprecated
    # def reset(self):
    #    self.conf = deepcopy(self.conf_bkp)


    def getSectionOfOption(self, optionName):

        for optionSection in self.conf:

            if optionName in self.conf[optionSection]:

                return optionSection

        return None


    def printOptions(self, section=None):
        if section and section in self.conf:
            self.pp.pprint(self.conf[section])
        else:
            self.pp.pprint(self.conf)


    def getOptionValue(self, optionName):

        optionSection = self.getSectionOfOption(optionName)

        if not optionSection:
            raise OptionNotFoundInConfigFileError("The option %s has not been found in the configuration."%(optionName))

        return self.conf[optionSection][optionName]


    def addOptions(self, section , **kwargs):
        """
        More generic than setOptions.
        """
        for optionName, optionValue in kwargs.items():
            if section not in self.conf:
                self.conf[section] = {}

            self.conf[section][optionName] = optionValue


    def setOptions(self, force=False, **kwargs):
        """

        """
        if "tmin" in kwargs and "timetype" not in kwargs:
            raise CannotSetNotUpdatableOptionError("The option 'tmin' can be updated if and only if you also specify the 'timetype' option.")
        if "tmax" in kwargs and "timetype" not in kwargs:
            raise CannotSetNotUpdatableOptionError("The option 'tmin' can be updated if and only if you also specify the 'timetype' option.")


        for optionName, optionValue in kwargs.items():

            optionSection = self.getSectionOfOption(optionName)

            if optionSection is None:
                raise OptionNotFoundInConfigFileError("Section '{}' not found in configuration file.".format(optionSection))

            if AgilepyConfig._notUpdatable(optionName):
                if not force:
                    raise CannotSetNotUpdatableOptionError("The option '{}' cannot be updated.".format(optionName))

            if AgilepyConfig._isHidden(optionName):
                raise CannotSetHiddenOptionError("Can't update the '{}' hidden option.".format(optionSection))


            isOk, errorMsg = AgilepyConfig._validateOptioNameAndValue(optionName, optionValue)

            if not isOk:
                raise ConfigFileOptionTypeError("Can't set config option '{}'. Error: {}".format(optionName, errorMsg))

            self.conf[optionSection][optionName] = optionValue

            if optionName == "loccl":

                AgilepyConfig._transformLoccl(self.conf)

            if optionName == "isocoeff" or optionName == "galcoeff":

                AgilepyConfig._convertBackgroundCoeff(self.conf, optionName)




        self.validateConfiguration()







    def getConf(self, key=None, subkey=None):
        if key and key in self.conf:
            if subkey and subkey in self.conf[key]:
                return self.conf[key][subkey]
            else:
                return self.conf[key]
        else:
            return self.conf


    @staticmethod
    def _getOptionExpectedTypes(optionName):
        """
        None if it does not exixst
        """

        # int
        if optionName in ["verboselvl", "filtercode", "emin", "emax", "fovradmin", \
                          "fovradmax", "albedorad", "dq", "phasecode", "expstep", \
                          "fovbinnumber", "galmode", "isomode", "emin_sources", \
                          "emax_sources", "loccl"]:
            return (None, Number)

        # Number
        if optionName in ["glat", "glon", "tmin", "tmax", "mapsize", "spectralindex", \
                          "timestep", "binsize", "ranal", "ulcl", \
                          "expratio_minthr", "expratio_maxthr", "expratio_size"]:
            return (None, Number)

        # String
        elif optionName in ["evtfile", "logfile", "outdir", "filenameprefix", "logfilenameprefix", \
                            "timetype", "timelist", "projtype", "proj", "modelfile"]:
            return (None, str)

        elif optionName in ["useEDPmatrixforEXP", "expratioevaluation", "twocolumns"]:
            return (None, bool)

        # List of Numbers
        elif optionName in ["energybins"]:
            return (List, List)

        # List of Numbers
        elif optionName in ["galcoeff", "isocoeff"]:
            return (List, Number)

        else:
            return (None, None)

    @staticmethod
    def _notUpdatable(optionName):
        if optionName in ["logfilenameprefix", "verboselvl"]:
            return True
        return False

    @staticmethod
    def _isHidden(optionName):

        if optionName in [ "lonpole", "lpointing", "bpointing", "maplistgen", "offaxisangle", \
                           "galmode2", "galmode2fit", "isomode2", "isomode2fit", "minimizertype", \
                           "minimizeralg", "minimizerdefstrategy", "mindefaulttolerance", "integratortype", \
                           "contourpoints", "edpcorrection", "fluxcorrection"]:
            return True

        return False


    @staticmethod
    def _validateOptioNameAndValue(optionName, optionValue):

        complexType, basicType = AgilepyConfig._getOptionExpectedTypes(optionName)

        if complexType is None and basicType is None:
            return (False, f"Something is wrong with complexType: {complexType} and basicType {basicType} of optionName: {optionName}")

        if complexType == List and not isinstance(optionValue, complexType):
            return (False, f"The option value {optionName} has not the expected data type {complexType} of {basicType}, but: {type(optionValue)}")

        if complexType == List:
            for idx, elem in enumerate(optionValue):
                if not isinstance(elem, basicType):
                    return (False, f"The {idx}th elem of {optionName} has not the expected data type {basicType}, but: {type(elem)}")
        elif complexType is None:
            if not isinstance(optionValue, basicType):
                return (False, f"The {optionName} has not the expected data type {basicType}, but: {type(optionValue)}")

        return (True, "")

    @staticmethod
    def _mergeConfigurations(dict1, dict2):
        """
        Merge dict2 (user defined conf) with dict1 (default conf) (this op is not symmetric)
        """
        merged = {}
        for sectionName in dict1.keys():
            merged[sectionName] = {}

        for sectionName in dict1.keys():
            for key in dict1[sectionName].keys():
                if sectionName in dict2 and key in dict2[sectionName].keys():
                    if key=="glon":
                        merged[sectionName]["glon"] = dict2[sectionName]["glon"] + 0.000001
                    else:
                        merged[sectionName][key] = dict2[sectionName][key]
                else:
                    merged[sectionName][key] = dict1[sectionName][key]

        return merged

    @staticmethod
    def _completeConfiguration(confDict):
        AgilepyConfig._convertEnergyBinsStrings(confDict)
        AgilepyConfig._convertBackgroundCoeff(confDict, "isocoeff")
        AgilepyConfig._convertBackgroundCoeff(confDict, "galcoeff")
        AgilepyConfig._setTime(confDict)
        AgilepyConfig._setPhaseCode(confDict)
        AgilepyConfig._setExpStep(confDict)
        AgilepyConfig._expandEnvVars(confDict)
        AgilepyConfig._transformLoccl(confDict)
        return confDict

    @staticmethod
    def _checkRequiredParams(confDict):

        errors = []

        if confDict["input"]["evtfile"] is None:
            errors.append("Please, set input/evtfile")

        if confDict["input"]["logfile"] is None:
            errors.append("Please, set input/logfile")

        if confDict["output"]["outdir"] is None:
            errors.append("Please, set output/outdir")

        if confDict["output"]["filenameprefix"] is None:
            errors.append("Please, set output/filenameprefix")

        if confDict["output"]["logfilenameprefix"] is None:
            errors.append("Please, set output/logfilenameprefix")

        if confDict["output"]["verboselvl"] is None:
            errors.append("Please, set output/verboselvl")

        if confDict["selection"]["timetype"] is None:
            errors.append("Please, set selection/timetype (MJD or TT)")

        if confDict["selection"]["tmin"] is None:
            errors.append("Please, set selection/tmin")

        if confDict["selection"]["tmax"] is None:
            errors.append("Please, set selection/tmax")

        if confDict["selection"]["glon"] is None:
            errors.append("Please, set selection/glon")

        if confDict["selection"]["glat"] is None:
            errors.append("Please, set selection/glat")

        if errors:
            raise ConfigurationsNotValidError("{}".format(errors))

    @staticmethod
    def _parseListNotation(strList):
        # check regular expression??
        return [float(elem.strip()) for elem in strList.split(',')]

    @staticmethod
    def _convertEnergyBinsStrings(confDict):
        l = []
        for stringList in confDict["maps"]["energybins"]:
            res = AgilepyConfig._parseListNotation(stringList)
            l.append([int(r) for r in res])
        confDict["maps"]["energybins"] = l

    @staticmethod
    def _convertBackgroundCoeff(confDict, bkgCoeffName):

        bkgCoeffVal = confDict["model"][bkgCoeffName]
        numberOfEnergyBins = len(confDict["maps"]["energybins"])
        fovbinnumber = confDict["maps"]["fovbinnumber"]
        numberOfMaps = numberOfEnergyBins*fovbinnumber

        # if None
        if bkgCoeffVal is None:
            confDict["model"][bkgCoeffName] = [-1 for i in range(numberOfMaps)]

        # if -1
        elif bkgCoeffVal == -1:
            confDict["model"][bkgCoeffName] = [-1 for i in range(numberOfMaps)]

        # if only one value
        elif isinstance(bkgCoeffVal, numbers.Number):
            confDict["model"][bkgCoeffName] = [bkgCoeffVal]

        # if comma separated values
        elif isinstance(bkgCoeffVal, str):
            confDict["model"][bkgCoeffName] = AgilepyConfig._parseListNotation(bkgCoeffVal)

        # if List
        elif isinstance(bkgCoeffVal, List):
            confDict["model"][bkgCoeffName] = bkgCoeffVal

        else:
            print(f"Something's wrong..bkgCoeffName: {bkgCoeffName}, bkgCoeffVal: {bkgCoeffVal}")
            confDict["model"][bkgCoeffName] = None



    @staticmethod
    def _setPhaseCode(confDict):
        if not confDict["selection"]["phasecode"]:
            if confDict["selection"]["tmax"] >= 182692800.0:
                confDict["selection"]["phasecode"] = 6 #SPIN
            else:
                confDict["selection"]["phasecode"] = 18 #POIN

    @staticmethod
    def _setTime(confDict):
        if confDict["selection"]["timetype"] == "MJD":
            confDict["selection"]["tmax"] = AstroUtils.time_mjd_to_tt(confDict["selection"]["tmax"])
            confDict["selection"]["tmin"] = AstroUtils.time_mjd_to_tt(confDict["selection"]["tmin"])
            confDict["selection"]["timetype"] = "TT"

    @staticmethod
    def _setExpStep(confDict):
        if not confDict["maps"]["expstep"]:
             confDict["maps"]["expstep"] = round(1 / confDict["maps"]["binsize"], 2)

    @staticmethod
    def _expandEnvVars(confDict):
        confDict["input"]["evtfile"] = AgilepyConfig._expandEnvVar(confDict["input"]["evtfile"])
        confDict["input"]["logfile"] = AgilepyConfig._expandEnvVar(confDict["input"]["logfile"])
        confDict["output"]["outdir"] = AgilepyConfig._expandEnvVar(confDict["output"]["outdir"])

    @staticmethod
    def _expandEnvVar(path):
        if "$" in path:
            expanded = expandvars(path)
            if expanded == path:
                print("[AgilepyConfig] Environment variable has not been expanded in {}".format(expanded))
                raise EnvironmentVariableNotExpanded("[AgilepyConfig] Environment variable has not been expanded in {}".format(expanded))
            else:
                return expanded
        else:
            return path

    @staticmethod
    def _transformLoccl(confDict):

        userLoccl = confDict["mle"]["loccl"]

        if userLoccl == 99:
            confDict["mle"]["loccl"] = 9.21034
        elif userLoccl == 95:
            confDict["mle"]["loccl"] = 5.99147
        elif userLoccl == 68:
            confDict["mle"]["loccl"] = 2.29575
        else:
            confDict["mle"]["loccl"] = 1.38629


    @staticmethod
    def _loadFromYaml(file):

        with open(file, 'r') as yamlfile:

            return yaml.safe_load(yamlfile)




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

        (first, last, lineSize) = AgilepyConfig._getFirstAndLastLineInFile(confDict["input"]["evtfile"])

        idxTmin = AgilepyConfig._extractTimes(first)[0]
        idxTmax = AgilepyConfig._extractTimes(last)[1]

        if lineSize > 1024:
            print("[AgilepyConfig] ! WARNING ! The byte size of the first input/evtfile line {} is {} B.\
                   This value is greater than 500. Please, check the evt index time range: TMIN: {} - TMAX: {}".format(firstLine, lineSize, tmin, tmax))

        userTmin = confDict["selection"]["tmin"]
        userTmax = confDict["selection"]["tmax"]

        if float(userTmin) < float(idxTmin):
            errors["input/tmin"]="tmin: {} is outside the time range of {} ( < idxTmin). Time range: [{}, {}]" \
                                  .format(confDict["selection"]["tmin"], confDict["input"]["evtfile"], idxTmin, idxTmax)

        if float(userTmin) > float(idxTmax):
            errors["input/tmin"]="tmin: {} is outside the time range of {} ( > idxTmax). Time range: [{}, {}]" \
                                  .format(confDict["selection"]["tmin"], confDict["input"]["evtfile"], idxTmin, idxTmax)


        if float(userTmax) > float(idxTmax):
            errors["input/tmax"]="tmax: {} is outside the time range of {} ( > idxTmax). Time range: [{}, {}]" \
                                  .format(confDict["selection"]["tmax"], confDict["input"]["evtfile"], idxTmin, idxTmax)

        if float(userTmax) < float(idxTmin):
            errors["input/tmax"]="tmax: {} is outside the time range of {} ( < idxTmin). Time range: [{}, {}]" \
                                  .format(confDict["selection"]["tmax"], confDict["input"]["evtfile"], idxTmin, idxTmax)


        return errors

    @staticmethod
    def _getFirstAndLastLineInFile(file):
        with open(file, 'rb') as evtindex:
            firstLine = next(evtindex).decode()
            lineSize = len(firstLine.encode('utf-8'))
            evtindex.seek(-500, os.SEEK_END)
            lastLine = evtindex.readlines()[-1].decode()
            return (firstLine, lastLine, lineSize)

    @staticmethod
    def _extractTimes(indexFileLine):
        elements = indexFileLine.split(" ")
        return (elements[1], elements[2])
