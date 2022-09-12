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

from pathlib import Path
from typing import List

from agilepy.utils.Observer import Observer

class MapList(Observer):
    def __init__(self, logger=None):
        self.logger = logger
        self.outputFilePath = None
        self.isEmpty = True
        self.ctsMap = []
        self.expMap = []
        self.gasMap = []
        self.bincenter = []
        self.galcoeff = []
        self.isocoeff = []

    def reset(self):
        self.outputFilePath = None
        self.isEmpty = True  
        self.ctsMap = []
        self.expMap = []
        self.gasMap = []
        self.bincenter = []
        self.galcoeff = []
        self.isocoeff = []

    def addRow(self, ctsMap, expMap, gasMap, bincenter, galcoeff, isocoeff):
        self.ctsMap.append(ctsMap)
        self.expMap.append(expMap)
        self.gasMap.append(gasMap)
        self.bincenter.append(str(bincenter))
        self.galcoeff.append(str(galcoeff))
        self.isocoeff.append(str(isocoeff))
        self.isEmpty = False

    def writeToFile(self):
        outputFilePath = self.getFile()
        if outputFilePath is not None:
            with open(outputFilePath, "w") as mlf:
                for idx,ctsmap in enumerate(self.ctsMap):
                    mlf.write(ctsmap+" "+self.expMap[idx]+" "+self.gasMap[idx]+" "+self.bincenter[idx]+" "+self.galcoeff[idx]+" "+self.isocoeff[idx]+"\n")

        if self.logger:
            self.logger.info(self, "Produced: %s", str(outputFilePath))

        return str(outputFilePath)

    def updateBkgCoeffs(self, galcoeff=None, isocoeff=None):

        if galcoeff is not None and isinstance(galcoeff, List) and len(galcoeff) == len(self.ctsMap):
            self.galcoeff = [str(g) for g in galcoeff]
            if self.logger:
                self.logger.info(self, f"Updating galactic coefficients: {self.galcoeff}")

        if isocoeff is not None and isinstance(isocoeff, List) and len(isocoeff) == len(self.ctsMap):
            self.isocoeff = [str(i) for i in isocoeff]
            if self.logger:
                self.logger.info(self, f"Updating isotropic coefficients: {self.isocoeff}")

        return self.writeToFile()

    

    def setFile(self, outputFilePath):
        self.outputFilePath = Path(outputFilePath).with_suffix(".maplist4")

    def getFile(self):
        return self.outputFilePath

    def update(self, type, newstate):
        if type == "galcoeff":
            self.updateBkgCoeffs(galcoeff=newstate)
        if type == "isocoeff":
            self.updateBkgCoeffs(isocoeff=newstate)
