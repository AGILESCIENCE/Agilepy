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
import os
import subprocess
from abc import ABC, abstractmethod

from agilepy.utils.Utils import AgilepyLogger

class ProcessWrapper(ABC):

    def __init__(self, exeName):

        self.logger = AgilepyLogger()
        self.exeName = exeName
        self.args = []

    @abstractmethod
    def setArguments(self, confDict):
        pass

    @abstractmethod
    def parseOutput(self):
        pass

    @abstractmethod
    def getOutputName(self, prefix):
        pass

    @abstractmethod
    def getRequiredOptions(self):
        pass

    def allRequiredOptionsSet(self, confDict, requiredOptions):
        ok = True
        for option in requiredOptions:
            if not confDict.getOptionValue(option):
                optionSection = confDict.getSectionOfOption(option)
                self.logger.critical(self,"Option '%s' of section '%s' has not been set.", [option, optionSection])
                ok = False
        return ok


    def call(self):

        self.logger.info(self, "Science tool called!", newline=True)

        # copy par file
        pfile_location = os.path.join(os.environ["AGILE"],"share")
        pfile = os.path.join(pfile_location,self.exeName+".par")

        command = "cp "+pfile+" ./"
        self.executeCommand(command)

        # starting the tool
        command = self.exeName + " " + " ".join(map(str, self.args))
        self.executeCommand(command)

        # remove par file
        command = "rm ./"+self.exeName+".par"
        self.executeCommand(command)


    def executeCommand(self, command):
        self.logger.info(self, "Executing command >> "+command)
        completedProcess = subprocess.run(command, shell=True, capture_output=True, encoding="utf8")
        if completedProcess.returncode != 0:
            self.logger.critical(self, "Non zero return status. stderr >>" + completedProcess.stderr.strip() )
            exit(1)
        # self.logger.info(self, "stout >>"+completedProcess.stdout)


class CtsMapGenerator(ProcessWrapper):

    def __init__(self, exeName):
        super().__init__(exeName)

    def getRequiredOptions(self):
        return ["evtfile", "outdir", "mapnameprefix", "emin", "emax", "energybins", "glat", "glon", "tmin", "tmax"]

    def setArguments(self, confDict):

        if not self.allRequiredOptionsSet(confDict, self.getRequiredOptions()):
            self.logger.critical(self,"Some options have not been set.")
            exit(1)

        outDir = confDict.getOptionValue("outdir")
        outputName = self.getOutputName(confDict.getOptionValue("mapnameprefix"))


        self.args = [ os.path.join(outDir, outputName),  \
                      confDict.getOptionValue("evtfile"), #indexfiler\
                      confDict.getOptionValue("timelist"), \
                      confDict.getOptionValue("mapsize"), \
                      confDict.getOptionValue("binsize"), \
                      confDict.getOptionValue("glon"), \
                      confDict.getOptionValue("glat"), \
                      confDict.getOptionValue("lonpole"), \
                      confDict.getOptionValue("albedorad"), \
                      confDict.getOptionValue("phasecode"), \
                      confDict.getOptionValue("filtercode"), \
                      confDict.getOptionValue("proj"), \
                      confDict.getOptionValue("tmin"), \
                      confDict.getOptionValue("tmax"), \
                      confDict.getOptionValue("emin"), \
                      confDict.getOptionValue("emax"), \
                      confDict.getOptionValue("fovradmin"), \
                      confDict.getOptionValue("fovradmax"), \
                    ]


    def parseOutput(self):
        pass

    def getOutputName(self, prefix):
        return prefix+".cts.gz"
