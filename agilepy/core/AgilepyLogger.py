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
import sys
import logging
from pathlib import Path
from time import strftime
from os.path import expandvars
from colorama import Fore, Back, Style

class Singleton(type):
    '''Make sure there is a single instance of the logger class at any time.'''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
       
# https://gist.github.com/joshbode/58fac7ababc700f51e2a9ecdebe563ad
class ColoredFormatter(logging.Formatter):

    def __init__(self, *args, colors=None, **kwargs):
        """Initialize the formatter with specified format strings."""

        super().__init__(*args, **kwargs)

        self.colors = colors if colors else {}

    def format(self, record) -> str:
        """Format the specified record as text."""

        record.color = self.colors.get(record.levelname, '')
        record.reset = Style.RESET_ALL

        return super().format(record)




class AgilepyLogger(metaclass=Singleton):
    '''This class defines the logging format, level and output.'''

    def __init__(self):
        self.formatter = ColoredFormatter(
            '{asctime} |{color} {levelname:8} {reset}| {name} | {message} | ({filename}:{lineno})',
            style='{', datefmt='%Y-%m-%d %H:%M:%S',
            colors={
                'DEBUG': Fore.CYAN,
                'INFO': Fore.GREEN,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
            }
        )
        self.logLevel = None
        self.rootLogsDir = None
        self.today = strftime('%Y%m%d')
        self.now = strftime('%H%M%S')

    @staticmethod
    def mapLogLevel(verboseLvl):
        if verboseLvl == 0:
            return logging.ERROR
        elif verboseLvl == 1:
            return logging.WARNING
        elif verboseLvl == 2:
            return logging.INFO
        elif verboseLvl == 3:
            return logging.DEBUG
        else:
            raise ValueError(f"Invalid value for verboseLvl ({verboseLvl}). Allowed values are 0 (ERROR), 1 (WARNING), 2 (INFO), 3 (DEBUG)")


    def setLogger(self, rootPath=None, logLevel=3):
        """
        Must be called once, before getLogger()
        It sets the root directory of the logs, the log level and the formatter. 
        It defines a common stream handler for all the loggers. (TODO: think about it in a multiprocessing/multithread context)
        """
        if rootPath is not None:
            self.rootLogsDir = Path(expandvars(rootPath)).joinpath("logs")
            self.rootLogsDir.mkdir(parents=True, exist_ok=True)
        
        self.logLevel = AgilepyLogger.mapLogLevel(logLevel)
        
        self.sh = logging.StreamHandler(sys.stdout)
        self.sh.setLevel(self.logLevel)
        self.sh.setFormatter(self.formatter)

        print(f"Log level set to {self.logLevel} and output to {self.rootLogsDir}")
        return self

    def getRootLogsDir(self):
        return self.rootLogsDir

    def getLogger(self, loggerName, id=None, addFileHandler=True):
        """
        Two different DQAnalysis processes can call this method with the same loggerName, 
        and they will get different loggers. (TODO: check if this is true).

        Each class used by a DQAnalysis process that needs to log something must call this method to get a logger.
        The loggerName must be the name of the class that calls this method.
        Since the loggerName is the same for all the instances of the same class for different DQAnalysis processes, 
        the loggerName must be unique for each class, then an ID is appended to the loggerName.
        
        We expect the loggerName to have the following format: <class_name>_<id>
        """
        if id is not None:
            logger = logging.getLogger(f"{loggerName}.{id}")
        else:
            logger = logging.getLogger(loggerName)

        logger.setLevel(self.logLevel)

        # avoid duplicating handlers   
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            logger.addHandler(self.sh)

        # We want each class to log in its own file.
        # We don't want to propagate the log events to the ancestors of the logger.
        logger.propagate = False


        if addFileHandler:

            if not self.rootLogsDir.exists():
                raise Exception(f"Log output directory {self.rootLogsDir} does not exist. Call setLogger() first.")

            if id is not None:
                loggerName += f"_{id}"

            loggerOutputDir = str(self.rootLogsDir.joinpath(loggerName+".log"))

            fh = logging.FileHandler(loggerOutputDir)
                
            fh.setLevel(self.logLevel)
            fh.setFormatter(self.formatter)

            # avoid duplicating handlers 
            if fh in logger.handlers:
                raise Exception(f"Logger already has a file handler {fh}")


            logger.addHandler(fh)

        return logger
    
    @staticmethod
    def getDefaultLogger(loggerName, logLevel):
        return AgilepyLogger() \
                        .setLogger(rootPath=None, logLevel=logLevel) \
                        .getLogger(loggerName, addFileHandler=False)
    



