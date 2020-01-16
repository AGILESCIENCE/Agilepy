"""
 DESCRIPTION
       Agilepy software

 NOTICE
       Any information contained in this software
       is property of the AGILE TEAM and is strictly
       private and confidential.
       Copyright (C) 2005-2020 AGILE Team.
           Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
           Addis Antonio <antonio.addis@inaf.it>
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


import os
import subprocess
from abc import ABC, abstractmethod

from agilepy.utils.Utils import agilepyLogger
from agilepy.utils.Parameters import Parameters

class ProcessWrapper(ABC):

    def __init__(self, exeName):

        self.logger = agilepyLogger
        self.exeName = exeName
        self.args = []
        self.outfilePath = None
        self.products = []
        self.callCounter = 0

    @abstractmethod
    def setArgumentsAndProducts(self, confDict):
        """
        This method must initialize the 'args' and 'products' attributes of the object.
        """
        pass

    @abstractmethod
    def getRequiredOptions(self):
        pass

    def allRequiredOptionsSet(self, confDict):
        ok = True
        for option in self.getRequiredOptions():
            if confDict.getOptionValue(option) is None:
                optionSection = confDict.getSectionOfOption(option)
                self.logger.critical(self,"Option '%s' of section '%s' has not been set.", [option, optionSection])
                ok = False
        return ok


    def call(self):

        self.logger.info(self, "Science tool called!", newline=True)

        if not self.args:
            self.logger.warning(self, "The 'args' attribute has not been set! Please, call setArguments() before call()! ", [])
            return []

        # copy par file
        pfile_location = os.path.join(os.environ["AGILE"],"share")
        pfile = os.path.join(pfile_location,self.exeName+".par")

        command = "cp "+pfile+" ./"
        self.executeCommand(command)

        # starting the tool
        command = self.exeName + " " + " ".join(map(str, self.args))
        toolstdout = self.executeCommand(command)

        # remove par file
        command = "rm ./"+self.exeName+".par"
        self.executeCommand(command)

        self.callCounter += 1

        products = []
        for product in self.products:
            if not os.path.isfile(product):
                self.logger.critical(self, "Product %s has NOT been produced by science tool. \n\nScience tool stdout: %s", [product, toolstdout])
                exit(1)
            else:
                products.append(product)

        return products


    def executeCommand(self, command):
        self.logger.info(self, "Executing command >> "+command)
        completedProcess = subprocess.run(command, shell=True, capture_output=True, encoding="utf8")
        if completedProcess.returncode != 0:
            self.logger.critical(self, "Non zero return status. stderr >>" + completedProcess.stderr.strip() )
            exit(1)
        return completedProcess.stdout
        # self.logger.info(self, "stout >>"+completedProcess.stdout)
