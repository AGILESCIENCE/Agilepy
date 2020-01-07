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

import subprocess
from abc import ABC, abstractmethod

class ProcessWrapper(ABC):

    def __init__(self, exeName, exeParams):
        pass

    @abstractmethod
    def call(self):
        pass

    @abstractmethod
    def parseOutput(self):
        pass

class ComputeFlux(ProcessWrapper):

    def __init__(self, exeName, exeParams):
        super().__init__(exeName, exeParams)

    def call(self):
        pass

    def parseOutput(self):
        pass

class ComputeTS(ProcessWrapper):

    def __init__(self, exeName, exeParams):
        super().__init__(exeName, exeParams)

    def call(self):
        pass

    def parseOutput(self):
        pass
