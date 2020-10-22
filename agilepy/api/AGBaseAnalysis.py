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
from time import strftime

from agilepy.config.AgilepyConfig import AgilepyConfig
from agilepy.utils.AgilepyLogger import AgilepyLogger
from agilepy.utils.PlottingUtils import PlottingUtils
from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies

from agilepy.utils.CustomExceptions import AGILENotFoundError, PFILESNotFoundError, ConfigurationsNotValidError



class AGBaseAnalysis:

    def __init__(self, configurationFilePath):

        self.config = AgilepyConfig()

        # load only "input" and "output" sections
        self.config.loadBaseConfigurations(configurationFilePath, validate=True)

        # Creating output directory

        self.outdir = self.config.getConf("output","outdir")+"_"+strftime("%Y%m%d-%H%M%S")

        self.config.setOptions(outdir=self.outdir, validate=False)

        Path(self.outdir).mkdir(parents=True, exist_ok=True)


        
        self.logger = AgilepyLogger()

        self.logger.initialize(self.outdir, self.config.getConf("output","logfilenameprefix"), self.config.getConf("output","verboselvl"))



        self.plottingUtils = PlottingUtils(self.config, self.logger)

        if "AGILE" not in os.environ:
            raise AGILENotFoundError("$AGILE is not set.")

        if "PFILES" not in os.environ:
            raise PFILESNotFoundError("$PFILES is not set.")


 