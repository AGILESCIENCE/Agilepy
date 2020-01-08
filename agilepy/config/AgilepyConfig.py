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
from os.path import dirname, realpath, join

from agilepy.utils.Utils import Singleton

class AgilepyConfig(metaclass=Singleton):
    """

    """
    def __init__(self, configurationFilePath = None):

        self.configurationFilePath = configurationFilePath

        currentDir = dirname(realpath(__file__))

        default_conf = self.loadFromYaml(join(currentDir,"./conf.default.yaml"))

        if self.configurationFilePath:

            user_conf = self.loadFromYaml(self.configurationFilePath)

        self.conf = {**default_conf, **user_conf} # user conf will ovveride default conf


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
