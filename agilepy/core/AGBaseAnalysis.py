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
from pathlib import Path
from shutil import rmtree

from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.utils.Utils import Utils
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.utils.PlottingUtils import PlottingUtils
from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies

from agilepy.core.CustomExceptions import AGILENotFoundError, PFILESNotFoundError, ConfigurationsNotValidError



class AGBaseAnalysis:

    def __init__(self, configurationFilePath):

        self.config = AgilepyConfig()

        # load only "input" and "output" sections
        self.config.loadBaseConfigurations(Utils._expandEnvVar(configurationFilePath))

        # Creating output directory

        self.outdir = self.config.getConf("output","outdir")

        Path(self.outdir).mkdir(parents=True, exist_ok=True)


        
        self.logger = AgilepyLogger()

        self.logger.initialize(self.outdir, self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))



        self.plottingUtils = PlottingUtils(self.config, self.logger)

        if "AGILE" not in os.environ:
            raise AGILENotFoundError("$AGILE is not set.")

        if "PFILES" not in os.environ:
            raise PFILESNotFoundError("$PFILES is not set.")


    def deleteAnalysisDir(self):

        """It deletes the output directory where all the products of the analysis are written.

        Args:

        Returns:
            True if the directory is succesfully deleted, False otherwise.

        """
        outDir = Path(self.config.getConf("output", "outdir"))

        if outDir.exists() and outDir.is_dir():
            rmtree(outDir)
            self.logger.info(self,"Analysis directory %s deleted.", str(outDir))
        else:
            self.logger.warning(self,"Output directory %s exists? %r is dir? %r", str(outDir), outDir.exists(), outDir.is_dir())
            return False

        return True



    def setOptions(self, **kwargs):
        """It updates configuration options specifying one or more key=value pairs at once.

        Args:
            kwargs: key-values pairs, separated by a comma.

        Returns:
            None

        Raises:
            ConfigFileOptionTypeError: if the type of the option value is not wrong.
            ConfigurationsNotValidError: if the values are not coherent with the configuration.
            CannotSetHiddenOptionError: if the option is hidden.
            OptionNotFoundInConfigFileError: if the option is not found.

        Note:
            The ``config`` attribute is initialized by reading the corresponding
            yaml configuration file, loading its contents in memory. Updating the values
            held by this object will not affect the original values written on disk.

        Example:

            >>> aganalysis.setOptions(mapsize=60, binsize=0.5)
            True

        """
        return self.config.setOptions(**kwargs)


    def getOption(self, optionName):
        """It reads an option value from the configuration.

        Args:
            optionName (str): the name of the option.

        Returns:
            The option value

        Raises:
            OptionNotFoundInConfigFileError: if the optionName is not found in the configuration.
        """

        return self.config.getOptionValue(optionName)


    def printOptions(self, section=None):
        """It prints the configuration options in the console.

        Args:
            section (str): you can specify a configuration file section to be printed out.

        Returns:
            None
        """
        return self.config.printOptions(section)