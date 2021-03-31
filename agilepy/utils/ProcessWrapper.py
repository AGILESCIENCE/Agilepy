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
import string
import random
import shutil
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod

from agilepy.core.CustomExceptions import ScienceToolProductNotFound, ScienceToolErrorCodeReturned

class ProcessWrapper(ABC):

    OPTIONAL_PRODUCT = 0
    REQUIRED_PRODUCT = 1

    def __init__(self, exeName, agilepyLogger):

        self.logger = agilepyLogger
        self.exeName = exeName
        self.args = []
        self.outputDir = None
        self.products = {} 
        self.callCounter = 0
        self.isAgileTool = True
        self.tmpDir = Path("/tmp/agilepy_tmp")

    @abstractmethod
    def configureTool(self, confDict, extraParams=None):
        """
        This method must initialize the 'args', 'products' and 'outputDir' attributes of the object.
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
                self.logger.critical(self,"Option '%s' of section '%s' has not been set.", option, optionSection)
                ok = False
        return ok

    def checkIfRequiredProductsAlreadyExist(self):
        count = 0
        for product in self.products:
            if os.path.isfile(product) and self.products[product] == ProcessWrapper.REQUIRED_PRODUCT:
                count +=1 

        requiredProducts = [filepath for filepath,isrequired in self.products.items() if isrequired == ProcessWrapper.REQUIRED_PRODUCT]
        requiredProductsNumber = len(requiredProducts)

        if count == requiredProductsNumber:
            self.logger.warning(self, f"{count} required products already exist.")
            return True
        elif count == 0:
            self.logger.debug(self, "No products exist yet")
            return False
        else:
            self.logger.critical(self, f"{count} required products already exist, but the expected required products number is {requiredProductsNumber}: {requiredProducts}")
            raise ScienceToolProductNotFound(f"{count} required products already exist, but the expected required products number is {requiredProductsNumber}: {requiredProducts}")

            
    
    def call(self):

        self.logger.info(self, "Science tool called!")

        if not self.args:
            self.logger.warning(self, "The 'args' attribute has not been set! Please, call setArguments() before call()! ")
            return []

        if self.checkIfRequiredProductsAlreadyExist():
            self.logger.warning(self, f"The {self.exeName} will not be called. Products already exists: \n{self.products}")
            return self.products

        Path(self.outputDir).mkdir(parents=True, exist_ok=True)

        if self.isAgileTool:
            # copy par file
            pfile_location = os.path.join(os.environ["AGILE"], "share")
            pfile = os.path.join(pfile_location,self.exeName+".par")

            tempDir = self.tmpDir.joinpath(''.join(random.choice(string.ascii_lowercase) for i in range(5)))
            tempDir.mkdir(parents=True, exist_ok=True)

            command = f"cp {pfile} {str(tempDir)}"

            self.executeCommand(command, printStdout=False)


        # starting the tool
        command = self.exeName + " " + " ".join(map(str, self.args))
        toolstdout = self.executeCommand(command)

        # remove temporary directory containing the par file copy 
        if self.isAgileTool:
            shutil.rmtree(str(tempDir))

        self.callCounter += 1

        products = []
        for product in self.products:
            if not os.path.isfile(product) and self.products[product] == ProcessWrapper.REQUIRED_PRODUCT:
                raise ScienceToolProductNotFound("Product %s has NOT been produced by science tool. \nScience tool stdout:\n\n%s"%(product, toolstdout))
            elif not os.path.isfile(product) and self.products[product] == ProcessWrapper.OPTIONAL_PRODUCT:
                products.append(None)
            else:
                products.append(product)


        self.logger.info(self, f"Science tool {self.exeName} produced:\n {products}")

        return products


    def executeCommand(self, command, printStdout=True):

        self.logger.debug(self, "Executing command >>%s ", command)

        completedProcess = subprocess.run(command, shell=True, capture_output=True, encoding="utf8")

        if completedProcess.returncode != 0:
            raise ScienceToolErrorCodeReturned("Non zero return status. \nstderr:" + completedProcess.stderr.strip())

        if printStdout:
            self.logger.debug(self, "Science tool stdout:\n\n%s\n\n", completedProcess.stdout)

        return completedProcess.stdout
