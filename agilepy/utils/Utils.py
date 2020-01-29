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
import math
from time import strftime

from agilepy.utils.CustomExceptions import LoggerTypeNotFound

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class AgilepyLogger(metaclass=Singleton):

    def __init__(self):
        self.debug_lvl = None
        self.logger = None
        self.initialized = False

    def initialize(self, outputDirectory, logFilenamePrefix, debug_lvl = 2):

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

        Path(outputDirectory).mkdir(parents=True, exist_ok=True)

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


class AstroUtils:

    @staticmethod
    def distance(ll,bl,lf,bf):

        if ll < 0 or ll > 360 or lf < 0 or lf > 360:
            return -2
        elif bl < -90 or bl > 90 or bf < -90 or bf > 90:
            return -2
        else:
            d1 = bl - bf
            d2 = ll - lf;

            bl1 = math.pi / 2.0 - (bl * math.pi  / 180.0)
            bf1 = math.pi / 2.0 - (bf * math.pi  / 180.0)
            m4 = math.cos(bl1) * math.cos(bf1)  + math.sin(bl1) * math.sin(bf1) * math.cos(d2 * math.pi  / 180.0);
            if m4 > 1:
                m4 = 1

            try:
                return math.acos(m4) *  180.0 / math.pi;

            except Exception as e:

                print("\nException in AstroUtils.distance (error in acos() ): ", e)
                
                return math.sqrt(d1*d1 + d2 * d2);

    @staticmethod
    def time_mjd_to_tt(timemjd):
        return (timemjd - 53005.0) *  86400.0

    @staticmethod
    def time_tt_to_mjd(timett):
        return (timett / 86400.0) + 53005.0

agilepyLogger = AgilepyLogger()
