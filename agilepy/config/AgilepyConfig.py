"""
 DESCRIPTION
       Agilepy software

 NOTICE
       Any information contained in this software
       is property of the AGILE TEAM and is strictly
       private and confidential.
       Copyright (C) 2005-2020 AGILE Team.
           Addis Antonio <antonio.addis@inaf.it>
           Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
           Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
           Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
       All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import yaml
import pprint
from os.path import dirname, realpath, join

from agilepy.utils.Utils import Singleton
from agilepy.utils.Utils import DataUtils

class AgilepyConfig(metaclass=Singleton):
    """

    """
    def __init__(self, configurationFilePath):

        self.pp = pprint.PrettyPrinter(indent=2)

        currentDir = dirname(realpath(__file__))

        default_conf = self.loadFromYaml(join(currentDir,"./conf.default.yaml"))

        user_conf = self.loadFromYaml(configurationFilePath)

        mergedConf = self.mergeConfigurations(default_conf, user_conf)

        self.conf = self.completeConfiguration(mergedConf)

    def mergeConfigurations(self, dict1, dict2):
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

    def completeConfiguration(self, confDict):
        self.convertEnergyBinsStrings(confDict)
        self.setTime(confDict)
        self.setPhaseCode(confDict)
        return confDict


    def convertEnergyBinsStrings(self, confDict):
        l = []
        for stringList in confDict["maps"]["energybins"]:
            res = stringList.strip('][').split(', ')
            l.append(res)
        confDict["maps"]["energybins"] = l



    def setPhaseCode(self, confDict):
        if not confDict["selection"]["phasecode"]:
            if confDict["selection"]["tmax"] >= 182692800.0:
                confDict["selection"]["phasecode"] = 6 #SPIN
            else:
                confDict["selection"]["phasecode"] = 18 #POIN


    def setTime(self, confDict):
        if confDict["selection"]["timetype"] == "MJD":
            confDict["selection"]["tmax"] = DataUtils.time_mjd_to_tt(confDict["selection"]["tmax"])
            confDict["selection"]["tmin"] = DataUtils.time_mjd_to_tt(confDict["selection"]["tmin"])
            confDict["selection"]["timetype"] = "TT"


    def getSectionOfOption(self, optionName):

        for optionSection in self.conf:

            if optionName in self.conf[optionSection]:

                return optionSection

        return None

    def printOptions(self):

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

    def loadFromYaml(self,file):

        with open(file, 'r') as yamlfile:

            try:

                return yaml.safe_load(yamlfile)

            except yaml.YAMLError as exc:

                print("[AgilepyConfig] exception:", exc)

                exit(1)
