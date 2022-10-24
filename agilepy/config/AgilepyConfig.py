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
from os.path import dirname, realpath, join
from pathlib import Path

from agilepy.config.AGAnalysisConfig import AGAnalysisConfig
from agilepy.config.AGEngAgileOffaxisVisibilityConfig import AGEngAgileOffaxisVisibilityConfig
from agilepy.config.AGEngAgileFermiOffAxisVisibilityComparisonConfig import AGEngAgileFermiOffAxisVisibilityComparisonConfig
from agilepy.config.AGAnalysisWaveletConfig import AGAnalysisWaveletConfig

from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies
from agilepy.utils.Observable import Observable
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.CustomExceptions import  ConfigurationsNotValidError, \
                                           OptionNotFoundInConfigFileError, \
                                           CannotSetNotUpdatableOptionError, \
                                           AnalysisClassNotSupported



class AgilepyConfig(Observable):
    """

    """
    def __init__(self):
        super().__init__()
        self.pp = pprint.PrettyPrinter(indent=2)
        self.initialized = False
        self.conf = None # the actual dictionary containing the key-value configuration pairs
        self.analysisConfig = None # contains the validation/completion logics for the analysis class


    @staticmethod
    def getCopy(copyFrom):
        ac = AgilepyConfig()
        ac.conf = deepcopy(copyFrom.conf)
        ac.analysisConfig = deepcopy(copyFrom.analysisConfig)
        ac.initialized = copyFrom.initialized
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

        if user_conf["output"]["sourcename"] is None:
            errors.append("Please, set output/sourcename")

        if user_conf["output"]["username"] is None:
            errors.append("Please, set output/username")

        if user_conf["output"]["verboselvl"] is None:
            errors.append("Please, set output/verboselvl")

        if errors:
            raise ConfigurationsNotValidError("{}".format(errors))

        CompletionStrategies._expandOutdirEnvVars(user_conf)
        CompletionStrategies._completeOutdirName(user_conf)

        self.conf = user_conf


    def loadConfigurationsForClass(self, className):

        if className == "AGAnalysis":
            
            self.analysisConfig = AGAnalysisConfig()

        elif className == "AGEngAgileOffaxisVisibility":

            self.analysisConfig = AGEngAgileOffaxisVisibilityConfig()


        elif className == "AGEngAgileFermiOffAxisVisibilityComparison":

            self.analysisConfig = AGEngAgileFermiOffAxisVisibilityComparisonConfig()

        elif className == "AGAnalysisWavelet":
            
            self.analysisConfig = AGAnalysisWaveletConfig()

        else:
            raise AnalysisClassNotSupported("The class: {} is not supported".format(className))

        self.analysisConfig.checkRequiredParams(self.conf)

        self.analysisConfig.completeConfiguration(self.conf)

        self.analysisConfig.validateConfiguration(self.conf)

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


    def setOptions(self, validate=True, **kwargs):
        
        # Base checks   
        for optionName, optionValue in kwargs.items():

            optionSection = self.getSectionOfOption(optionName)

            if optionSection is None:
                raise OptionNotFoundInConfigFileError("Section '{}' not found in configuration file.".format(optionSection))

            if AgilepyConfig._notUpdatable(optionName):
                raise CannotSetNotUpdatableOptionError("The option '{}' cannot be updated.".format(optionName))

        self.analysisConfig.checkOptions(**kwargs)

        # Analysis class config checks
        self.analysisConfig.checkOptionsType(**kwargs)

        confBKP = self.conf.copy()

        # Update the values!
        for optionName, optionValue in kwargs.items():
            
            optionSection = self.getSectionOfOption(optionName)

            confBKP[optionSection][optionName] = optionValue
            
            # Completion strategies
            self.analysisConfig.completeUpdate(optionName, confBKP)

        # Validation strategies
        errors = self.analysisConfig.validateConfiguration(confBKP)

        if errors:
            confBKP = None
            raise ConfigurationsNotValidError(f"Errors: {errors}")

        # Use confBKP 
        self.conf = confBKP.copy()


        # Notify the observables
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
    def _notUpdatable(optionName):
        if optionName in ["userestapi", "datapath", "logfilenameprefix", "verboselvl"]:
            return True
        return False


    @staticmethod
    def _loadFromYaml(file):

        with open(file, 'r') as yamlfile:

            return yaml.safe_load(yamlfile)


