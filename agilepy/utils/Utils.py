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
import sys
import logging
from os.path import join
from pathlib import Path

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

class AgilepyLogger(metaclass=Singleton):

    def __init__(self, outputDirectory = None, logFilename = None, debug_lvl = 2, init = False):

        if not init:
            return

        self.debug_lvl = debug_lvl

        # WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
        if self.debug_lvl == 0: debug_lvl_enum = logging.WARNING

        # INFO: Confirmation that things are working as expected.
        if self.debug_lvl == 1: debug_lvl_enum = logging.INFO

        # DEBUG: Detailed information, typically of interest only when diagnosing problems.
        if self.debug_lvl == 2: debug_lvl_enum = logging.DEBUG

        Path(outputDirectory).mkdir(parents=True, exist_ok=True)

        if logFilename:

            logFilename = join(outputDirectory, logFilename)


            logging.basicConfig(  format='%(asctime)s %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p',
                                  filename=logFilename, filemode='w', level=debug_lvl_enum
                               )
        else:

            logging.basicConfig(  format='%(asctime)s %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p',
                                  stream=sys.stdout, level=debug_lvl_enum
                               )

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(debug_lvl_enum)

        self.logger.info("[INFO   ] [%s] Logger is active. Logfile: %s", type(self).__name__, logFilename)

    def critical(self, context, message, arguments=[], newline=False):
        if newline: print("\n")
        self.logger.critical("[ERROR  ] [%s] " + message, type(context).__name__, *arguments)

    def info(self, context, message, arguments=[], newline=False):
        if newline: print("\n")
        self.logger.info("[INFO   ] [%s] " + message, type(context).__name__, *arguments)

    def warning(self, context, message, arguments=[], newline=False):
        if newline: print("\n")
        self.logger.warning("[WARNING] [%s] " + message, type(context).__name__, *arguments)

    def debug(self, context, message, arguments=[], newline=False):
        if newline: print("\n")
        self.logger.debug("[DEBUG  ] [%s] " + message, type(context).__name__, *arguments)


class DataUtils:

    @staticmethod
    def time_mjd_to_tt(timemjd):
        return (timemjd - 53005.0) *  86400.0

    @staticmethod
    def time_tt_to_mjd(timett):
        return (timett / 86400.0) + 53005.0
