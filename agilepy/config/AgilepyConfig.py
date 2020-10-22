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
from os.path import dirname, realpath, join
from pathlib import Path

from agilepy.config.AGAnalysisConfig import AGAnalysisConfig
from agilepy.config.AGEngVisibility1Config import AGEngVisibility1Config
from agilepy.config.AGEngVisibility2Config import AGEngVisibility2Config

from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies
from agilepy.utils.Observable import Observable
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.utils.CustomExceptions import  ConfigurationsNotValidError, \
                                            OptionNotFoundInConfigFileError, \
                                            ConfigFileOptionTypeError, \
                                            CannotSetHiddenOptionError, \
                                            CannotSetNotUpdatableOptionError, \
                                            AnalysisClassNotSupported



class AgilepyConfig(Observable):
    """

    """
    def __init__(self):
        super().__init__()
        self.pp = pprint.PrettyPrinter(indent=2)
        self.initialized = False
        self.conf = None


    @staticmethod
    def getCopy(copyFrom):
        ac = AgilepyConfig()
        ac.conf = deepcopy(copyFrom.conf)
        ac.initialized = True
        return ac


    def loadBaseConfigurations(self, configurationFilePath):

        user_conf = AgilepyConfig._loadFromYaml(configurationFilePath)
        

        errors = []

        if user_conf["output"]["outdir"] is None:
            errors.append("Please, set output/outdir")

        if user_conf["output"]["filenameprefix"] is None:
            errors.append("Please, set output/filenameprefix")

        if user_conf["output"]["logfilenameprefix"] is None:
            errors.append("Please, set output/logfilenameprefix")

        if user_conf["output"]["verboselvl"] is None:
            errors.append("Please, set output/verboselvl")

        if errors:
            raise ConfigurationsNotValidError("{}".format(errors))

        CompletionStrategies._expandOutdirEnvVars(user_conf)

        self.conf = user_conf


    def loadConfigurationsForClass(self, className):

        if className == "AGAnalysis":
            
            AGAnalysisConfig.checkRequiredParams(self.conf)

            AGAnalysisConfig.completeConfiguration(self.conf)

            AGAnalysisConfig.validateConfiguration(self.conf)


        elif className == "AGEngVisibility1":

            AGEngVisibility1Config.checkRequiredParams(self.conf)

            AGEngVisibility1Config.completeConfiguration(self.conf)

            AGEngVisibility1Config.validateConfiguration(self.conf)


        elif className == "AGEngVisibility2":

            AGEngVisibility2Config.checkRequiredParams(self.conf)

            AGEngVisibility2Config.completeConfiguration(self.conf)

            AGEngVisibility2Config.validateConfiguration(self.conf)

        else:
            raise AnalysisClassNotSupported("The class: {} is not supported".format(className))

        self.initialized = True


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


    def setOptions(self, force=False, validate=True, **kwargs):
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

                CompletionStrategies._transformLoccl(self.conf)

            if optionName == "isocoeff" or optionName == "galcoeff":

                CompletionStrategies._convertBackgroundCoeff(self.conf, optionName)

            if optionName == "energybins" or optionName == "fovbinnumber":

                CompletionStrategies._extendBackgroundCoeff(self.conf)
        
        # TODO VALIDARE I CAMPI!! (validamiiiiii)

        for optionName, optionValue in kwargs.items():

            optionSection = self.getSectionOfOption(optionName)

            self.notify(optionName, self.conf[optionSection][optionName])


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
    def _loadFromYaml(file):

        with open(file, 'r') as yamlfile:

            return yaml.safe_load(yamlfile)


