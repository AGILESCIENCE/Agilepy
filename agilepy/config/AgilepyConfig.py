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

from agilepy.utils.Utils import Singleton

class AgilepyConfig(metaclass=Singleton):
    """

    """
    def __init__(self, configurationFilePath):

        self.configurationFilePath = configurationFilePath

        with open(configurationFilePath, 'r') as yamlfile:

            try:

                self.conf = yaml.safe_load(yamlfile)

            except yaml.YAMLError as exc:

                print("[AgilepyConfig] exception:", exc)

                exit(1)

    def getConf(self, key=None):
        if not key:
            return self.conf
        else: return self.conf[key]
