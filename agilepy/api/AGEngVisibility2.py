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

from agilepy.api.AGBaseAnalysis import AGBaseAnalysis

from agilepy.external_packages.offaxis.create_offaxis_plot import *
from agilepy.external_packages.offaxis import create_offaxis_plot, agilecheck, fermicheck
from agilepy.external_packages.ap.APDisplayAGILEFermiComparison import *
from agilepy.utils.Utils import Utils, expandvars
from pathlib import Path
from agilepy.utils.CustomExceptions import EnvironmentVariableNotExpanded


class AGEngVisibility2(AGBaseAnalysis):
    """This class contains the high-level API methods to run offaxis and offaxis_ap_comparison tools. It's a AGEng subclass"""
    
    def __init__(self, configurationFilePath):
        """AGEngVisibility2 constructor.

        Args:
            configurationFilePath (str): the relative or absolute path to the yaml configuration file.

        Example:
            >>> from agilepy.api import AGEngVisibility2
            >>> ageng = AGEngVisibility2('agconfig.yaml')

        """
        super().__init__(configurationFilePath)

        self.config.loadConfigurationsForClass("AGEngVisibility2")

       



    def visibilityPlot2(self, time_windows, ra, dec, fermi_datapath, agile_datapath, run, zmax, mode=all, step=1):
        """It runs offaxis tools and creates a directory containing the result files
        
        Args:
            time_windws (2d float Array): It contains the tstart-tstop intervals to process the data, the structure has developed as a 2d array(eg [[t1,t2],[t3, t4], ..., [tn-1, tn]])
            ra (float): ra value
            dec (float): dec value
            fermi_datapath (str): fermi log filepath
            agile_datapath (str): agile log filepath
            run (integer): run number
            zmax (float): maximum offaxis degrees
            mode (str): options "agile" | "fermi" | "all": Select all to plot both data, otherwise it will plot only agile/fermi data 
            step (float): step value for plotting
        
        Returns:
            dir (str): A new directory containing the results
        """
        self.outdir = self.config.getOptionValue("outdir")

        agile_datapath = Utils._expandEnvVar(agile_datapath)
        fermi_datapath = Utils._expandEnvVar(fermi_datapath)


        offaxis = Create_offaxis_plot(time_windows, ra, dec, fermi_datapath, agile_datapath, run, zmax, mode, step, outdir = self.outdir)

        dir = offaxis.run()

        self.logger.info(self,"Output directory: %s", dir)

        return dir

    def apOffaxisComparation(self, agile_pathAP, fermi_pathAP, tstart, tstop, path_offaxis,lines = [], plotrate=False):
        """ It compares and shows aperture photometry data with offaxis results

        Args:
            agile_pathAP (str): agile ap filepath
            fermi_pathAP (str): fermi ap filepath
            tstart (float): time start in MJD
            tstop (float): time stop in MJD
            path_offaxis (str): directory path to offaxis results
            lines (list): 
            plotrate (bool): if true select column rate instead of counts

        return:
            void

        """

        comparison = APDisplayAGILEFermiComparison()

        comparison.load_and_plot(agile_pathAP, fermi_pathAP, tstart, tstop, path_offaxis, lines, plotrate)



    @staticmethod
    def getConfiguration(confFilePath, userName, outputDir, verboselvl):
        """Utility method to create a configuration file.

        Args:
            confFilePath (str): the path and filename of the configuration file that is going to be created.
            userName (str): the username of who is running the software.
            outputDir (str): the path to the output directory. The output directory will be created using the following format: 'userName_sourceName_todaydate'
            verboselvl (int): the verbosity level of the console output. Message types: level 0 => critical, warning, level 1 => critical, warning, info, level 2 => critical, warning, info, debug

        Raises:
            EnvironmentVariableNotExpanded: if an environmental variabile is found into a configuration path but it cannot be expanded.
            FileNotFoundError: if the evtfile of logfile are not found.
            ConfigurationsNotValidError: if at least one configuration value is bad.

        Returns:
            None
        """
        analysisname = userName

        if "$" in outputDir:
            expandedOutputDir = expandvars(outputDir)

            if expandedOutputDir == outputDir:
                print(f"Environment variable has not been expanded in {outputDir}")
                raise EnvironmentVariableNotExpanded(f"Environment variable has not been expanded in {outputDir}")

        outputDir = Path(expandedOutputDir).joinpath(analysisname)

        configuration = """
output:
  outdir: %s
  filenameprefix: %s_product
  logfilenameprefix: %s_log
  verboselvl: %d

        """%(str(outputDir), analysisname, analysisname, verboselvl)

        with open(confFilePath,"w") as cf:

            cf.write(configuration)



    @staticmethod
    def checkRequiredParams(confDict):
        pass
    
    @staticmethod
    def completeConfiguration(confDict):
        pass

    @staticmethod
    def validateConfiguration(confDict):
        pass