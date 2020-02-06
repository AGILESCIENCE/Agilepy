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
from os.path import join
from pathlib import Path
from time import strftime

from agilepy.utils.CustomExceptions import LoggerTypeNotFound
from agilepy.utils.Utils import Singleton

class AgilepyLogger(metaclass=Singleton):

    def __init__(self):
        self.debug_lvl = None
        self.logger = None
        self.initialized = False

    def initialize(self, outputDirectory, logFilenamePrefix, debug_lvl = 2):

        if self.initialized:

            return Path(self.logfilePath)

        self.debug_lvl = debug_lvl

        # CRITICAL: always present in the log.

        # WARNING: An indication that something unexpected happened, or indicative
        # of some problem in the near future (e.g. ‘disk space low’). The software is
        # still working as expected.
        if self.debug_lvl == 0: debug_lvl_enum = logging.WARNING

        # INFO: Confirmation that things are working as expected.
        if self.debug_lvl == 1: debug_lvl_enum = logging.INFO

        # DEBUG: Detailed information, typically of interest only when diagnosing problems.
        if self.debug_lvl == 2: debug_lvl_enum = logging.DEBUG

        Path(join(outputDirectory,"logs")).mkdir(parents=True, exist_ok=True)

        logFilenamePrefix = logFilenamePrefix+"_"+strftime("%Y%m%d-%H%M%S")

        self.logfilePath = join(outputDirectory, logFilenamePrefix+".log")


        # formatter
        logFormatter = logging.Formatter("%(asctime)s [%(levelname)-8.8s] %(message)s")


        self.consoleLogger = self.setup_logger("Console logger", "console", logFormatter, debug_lvl_enum)

        self.fileLogger = self.setup_logger("File logger", "file", logFormatter, logging.DEBUG, "{0}/{1}.log".format(outputDirectory, logFilenamePrefix))

        self.fileLogger.info("[%s] File and Console loggers are active. Log file: %s", type(self).__name__, self.logfilePath)
        self.consoleLogger.info("[%s] File and Console loggers are active. Log file: %s", type(self).__name__, self.logfilePath)

        self.initialized = True

        return Path(self.logfilePath)

    def setup_logger(self, name, type, formatter, level, log_file=None):
        """To setup as many loggers as you want"""

        if type == "file":
            handler = logging.FileHandler(log_file)

        elif type== "console":
            handler = logging.StreamHandler(sys.stdout)

        else:
            raise LoggerTypeNotFound("Logger of type %s is not supported"%(type))

        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger

    def critical(self, context, message, *arguments):
        if not self.initialized: return
        self.fileLogger.critical("[%s] " + message, type(context).__name__, *arguments)
        self.consoleLogger.critical("[%s] " + message, type(context).__name__, *arguments)

    def info(self, context, message, *arguments):
        if not self.initialized: return
        self.fileLogger.info("[%s] " + message, type(context).__name__, *arguments)
        self.consoleLogger.info("[%s] " + message, type(context).__name__, *arguments)

    def warning(self, context, message, *arguments):
        if not self.initialized: return
        self.fileLogger.warning("[%s] " + message, type(context).__name__, *arguments)
        self.consoleLogger.warning("[%s] " + message, type(context).__name__, *arguments)

    def debug(self, context, message, *arguments):
        if not self.initialized: return
        self.fileLogger.debug("[%s] " + message, type(context).__name__, *arguments)
        self.consoleLogger.debug("[%s] " + message, type(context).__name__, *arguments)

    def reset(self):
        if self.initialized:

            self.fileLogger.info("[%s] Removing logger...", type(self).__name__)
            for handler in self.fileLogger.handlers[:]:
                self.fileLogger.removeHandler(handler)

            self.consoleLogger.info("[%s] Removing logger...", type(self).__name__)
            for handler in self.consoleLogger.handlers[:]:
                self.consoleLogger.removeHandler(handler)



agilepyLogger = AgilepyLogger()
