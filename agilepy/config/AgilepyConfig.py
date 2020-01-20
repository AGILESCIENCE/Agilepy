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


import yaml
import pprint
import numbers
from copy import deepcopy
from os.path import dirname, realpath, join, expandvars

from agilepy.utils.Utils import Singleton, DataUtils


class AgilepyConfig(metaclass=Singleton):
    """

    """
    def __init__(self, configurationFilePath):

        self.pp = pprint.PrettyPrinter(indent=2)

        currentDir = dirname(realpath(__file__))

        default_conf = self._loadFromYaml(join(currentDir,"./conf.default.yaml"))

        user_conf = self._loadFromYaml(configurationFilePath)

        mergedConf = self._mergeConfigurations(default_conf, user_conf)

        self.conf = self._completeConfiguration(mergedConf)

        self.conf_bkp = deepcopy(self.conf)


    def reset(self):
        self.conf = deepcopy(self.conf_bkp)

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
            return None

        return self.conf[optionSection][optionName]


    def addOptions(self, section , **kwargs):
        """
        More generic than setOptions.
        """
        for optionName, optionValue in kwargs.items():
            if section not in self.conf:
                self.conf[section] = {}

            self.conf[section][optionName] = optionValue


    def setOptions(self, **kwargs):
        """
        Returns a dictionary of rejected parameters
        """
        rejected = {}

        for optionName, optionValue in kwargs.items():

            optionSection = self.getSectionOfOption(optionName)

            if optionSection:

                self.conf[optionSection][optionName] = optionValue

            else:

                rejected[optionName] = optionValue

        return rejected


    def getConf(self, key=None, subkey=None):
        if key and key in self.conf:
            if subkey and subkey in self.conf[key]:
                return self.conf[key][subkey]
            else:
                return self.conf[key]
        else:
            return self.conf






    """
        PRIVATE API
    """
    def _mergeConfigurations(self, dict1, dict2):
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


    def _completeConfiguration(self, confDict):
        self._convertEnergyBinsStrings(confDict)
        self._convertBackgroundCoeff(confDict)
        self._setTime(confDict)
        self._setPhaseCode(confDict)
        self._setExpStep(confDict)
        self._checkBackgroundCoeff(confDict)
        self._expandEnvVars(confDict)
        return confDict

    def _parseListNotation(self, str):
        # check regular expression??
        return [float(elem.strip()) for elem in str.split(',')]


    def _convertEnergyBinsStrings(self, confDict):
        l = []
        for stringList in confDict["maps"]["energybins"]:
            res = self._parseListNotation(stringList)
            l.append([int(r) for r in res])
        confDict["maps"]["energybins"] = l

    def _convertBackgroundCoeff(self, confDict):

        isocoeffVal = confDict["model"]["isocoeff"]
        numberOfEnergyBins = len(confDict["maps"]["energybins"])

        if isocoeffVal != -1:

            if isinstance(isocoeffVal, numbers.Number):
                confDict["model"]["isocoeff"] = [isocoeffVal]
            else:
                confDict["model"]["isocoeff"] = self._parseListNotation(isocoeffVal)

        else:

            confDict["model"]["isocoeff"] = [-1 for i in range(numberOfEnergyBins)]


        galcoeffVal = confDict["model"]["galcoeff"]

        if galcoeffVal != -1:

            if isinstance(galcoeffVal, numbers.Number):
                confDict["model"]["galcoeff"] = [galcoeffVal]
            else:
                confDict["model"]["galcoeff"] = self._parseListNotation(galcoeffVal)

        else:

            confDict["model"]["galcoeff"] = [-1 for i in range(numberOfEnergyBins)]

    def _checkBackgroundCoeff(self, confDict):

        numberOfEnergyBins = len(confDict["maps"]["energybins"])

        numberOfIsoCoeff = len(confDict["model"]["isocoeff"])

        if numberOfIsoCoeff != numberOfEnergyBins:

            print("[AgilepyConfig] numberOfEnergyBins (%d) is not equal to numberOfIsoCoeff (%d)" % (numberOfEnergyBins, numberOfIsoCoeff))
            exit(1)

        numberOfGalCoeff = len(confDict["model"]["galcoeff"])

        if numberOfGalCoeff != numberOfEnergyBins:

            print("[AgilepyConfig] numberOfEnergyBins (%d) is not equal to numberOfGalCoeff (%d)" % (numberOfEnergyBins, numberOfGalCoeff))
            exit(1)



    def _setPhaseCode(self, confDict):
        if not confDict["selection"]["phasecode"]:
            if confDict["selection"]["tmax"] >= 182692800.0:
                confDict["selection"]["phasecode"] = 6 #SPIN
            else:
                confDict["selection"]["phasecode"] = 18 #POIN


    def _setTime(self, confDict):
        if confDict["selection"]["timetype"] == "MJD":
            confDict["selection"]["tmax"] = DataUtils.time_mjd_to_tt(confDict["selection"]["tmax"])
            confDict["selection"]["tmin"] = DataUtils.time_mjd_to_tt(confDict["selection"]["tmin"])
            confDict["selection"]["timetype"] = "TT"


    def _setExpStep(self, confDict):
        if not confDict["maps"]["expstep"]:
             confDict["maps"]["expstep"] = round(1 / confDict["maps"]["binsize"], 2)

    def _expandEnvVars(self, confDict):
        confDict["input"]["evtfile"] = self._expandEnvVar(confDict["input"]["evtfile"])
        confDict["input"]["logfile"] = self._expandEnvVar(confDict["input"]["logfile"])
        confDict["output"]["outdir"] = self._expandEnvVar(confDict["output"]["outdir"])

    def _expandEnvVar(self, path):
        if "$" in path:
            expanded = expandvars(path)
            if expanded == path:
                print("[AgilepyConfig] Environment variable has not been expanded in {}".format(expanded))
                exit(1)
            else:
                return expanded
        else:
            return path


    def _loadFromYaml(self,file):

        with open(file, 'r') as yamlfile:

            return yaml.safe_load(yamlfile)
