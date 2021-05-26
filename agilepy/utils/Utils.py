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
from os.path import expandvars


from agilepy.core.CustomExceptions import EnvironmentVariableNotExpanded

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class Utils:

    @staticmethod
    def _expandEnvVar(path):
        if "$" in path:
            expanded = expandvars(path)
            if expanded == path:
                print(f"[CompletionStrategies] Environment variable has not been expanded in {expanded}")
                raise EnvironmentVariableNotExpanded(f"[CompletionStrategies] Environment variable has not been expanded in {expanded}")
            else:
                return expanded
        else:
            return path


    @staticmethod
    def _parseListNotation(strList):
        # check regular expression??
        return [float(elem.strip()) for elem in strList.split(',')]

    @staticmethod
    def _getFirstAndLastLineInFile(file):
        with open(file, 'rb') as evtindex:
            firstLine = next(evtindex).decode()
            lineSize = len(firstLine.encode('utf-8'))
            evtindex.seek(-lineSize, os.SEEK_END)
            lastLine = evtindex.readlines()[-1].decode()
            return (firstLine, lastLine)

    @staticmethod
    def _extractTimes(indexFileLine):
        elements = indexFileLine.split()
        return (elements[1], elements[2])
    
    @staticmethod
    def _createNextSubDir(path):
        subDirectories = next(os.walk(path))[1]
        currentOutputDirectories = sorted([int(name) for name in subDirectories if path.joinpath(name).is_dir()]) # [0, 1, 2, ]
        if not currentOutputDirectories: currentOutputDirectories = [-1] 
        path = path.joinpath(str(currentOutputDirectories[-1] + 1)) # 2+1
        path.mkdir(exist_ok=True)
        return path
