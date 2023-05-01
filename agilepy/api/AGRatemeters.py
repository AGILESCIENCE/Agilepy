# DESCRIPTION


import os
import re
from time import time
from pathlib import Path
from shutil import rmtree
from ntpath import basename
from os.path import join, splitext, expandvars

from agilepy.core.AGDataset import AGDataset
pattern = re.compile('e([+\-]\d+)')

from agilepy.core.AGBaseAnalysis import AGBaseAnalysis
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.ScienceTools import Multi

from agilepy.core.MapList import MapList
from agilepy.utils.Utils import Utils
from agilepy.core.CustomExceptions import   AGILENotFoundError, \
                                            PFILESNotFoundError, \
                                            ScienceToolInputArgMissing, \
                                            MaplistIsNone, SelectionParamNotSupported, \
                                            SourceNotFound, \
                                            SourcesLibraryIsEmpty, \
                                            ValueOutOfRange
                                            
class AGRatemeters(AGBaseAnalysis):
    """
    This class contains the high-level API to run analysis of the AGILE Ratemeters.
    
    The constructor of this class requires a ``yaml configuration file``.
    """
       
    
    def __init__(self, configurationFilePath):
        """AGRatemeters constructor.

        Args:
            configurationFilePath (str): a relative or absolute path to the yaml configuration file.

        Raises:
            AGILENotFoundError: if the AGILE environment variable is not set.
            PFILESNotFoundError: if the PFILES environment variable is not set.

        Example:
            >>> from agilepy.api import AGRatemeters
            >>> agratemeters = AGratemeters('agconfig.yaml')

        """
        super().__init__(configurationFilePath)
        
        self.config.loadConfigurationsForClass("AGRatemeters")

        self.logger = self.agilepyLogger.getLogger(__name__)

        # Should I keep these two?
        # MapList Observes the observable AgilepyConfig
        #self.currentMapList = MapList(self.logger)
        #self.multiTool = Multi("AG_multi", self.logger)
            
        return None


    def destroy(self):
        """ It clears the list of sources and the current maplist file.
        """        
        pass
    

    @staticmethod
    def getConfiguration(
                    confFilePath,
                    userName,
                    outputDir,
                    verboselvl,
                    timetype,
                    indexfile,
                    # evtfile="/AGILE_PROC3/FM3.119_ASDC2/INDEX/EVT.index",
                    # logfile="/AGILE_PROC3/DATA_ASDC2/INDEX/LOG.log.index"
                    contact,
                    T0,
                    tmin,
                    tmax,
                    tmin_bkg,
                    tmax_bkg,
                    tmin_src,
                    tmax_src,
                    flag_detrending,
                    sourceName,
                    flag_N_RM,
        ):
        """Utility method to create a configuration file.

        Args:
            confFilePath (str): the path and filename of the configuration file that is going to be created.
            userName (str): the username of who is running the software.
            outputDir (str): the path to the output directory. The output directory will be created using the following format: 'userName_sourceName_todaydate'
            verboselvl (int): the verbosity level of the console output. Message types: level 0 => critical, warning, level 1 => critical, warning, info, level 2 => critical, warning, info, debug
            indexfile (str): the index file to be used to search for AGILE cor3913 files.
            timetype (str): timetype format.
            contact (str): contact number.
            T0 (str): reference time of the analysis.
            tmin (float): the start time of the analysis window, in seconds with respect to T0.
            tmax (float): the stop time of the analysis window, in seconds with respect to T0.
            tmin_bkg (float): the start time of the background window, in seconds with respect to T0.
            tmax_bkg (float): the stop time of the background window, in seconds with respect to T0.
            tmin_src (float): the start time of the source window, in seconds with respect to T0.
            tmax_src (float): the stop time of the source window, in seconds with respect to T0.
            flag_detrending (str): \'D\' for data normalized by detrending algorithm, \'ND\' for not-detrended data. 
            sourceName (str): the name of the source.
            flag_N_RM (str): \'3M\' for Ratemeters of SA, MCAL, ACTop. \'8M\' to include also GRID and the four ACLats.

        Returns:
            None
        """

        configuration = f"""
input:
  indexfile: {indexfile}
          
output:
  outdir: {outputDir}
  filenameprefix: ratemeters_product
  logfilenameprefix: ratemeters_log
  sourcename: {sourceName}
  username: {userName}
  verboselvl: {verboselvl} 

selection:
  timetype: {timetype}
  contact: {contact}
  T0: {T0}
  tmin: {tmin}
  tmax: {tmax}
  tmin_bkg: {tmin_bkg}
  tmax_bkg: {tmax_bkg}
  tmin_src: {tmin_src}
  tmax_src: {tmax_src}
  flag_detrending: {flag_detrending}
  sourcename: {sourceName}
  flag_N_RM: {flag_N_RM}

        """

        with open(Utils._expandEnvVar(confFilePath),"w") as cf:

            cf.write(configuration)
        
        return None
    
    
    def run_ratemeters_script(self):
        """
        Run ratemeters scripts.
        """
        self.logger.info("Running ratemeters script")
        
        # Get the value of the parameters for the script
        T0=self.getOption('T0')
        tmin=self.getOption('tmin')
        tmax=self.getOption('tmax')
        tmin_bkg=self.getOption('tmin_bkg')
        tmax_bkg=self.getOption('tmax_bkg')
        tmin_src=self.getOption('tmin_src')
        tmax_src=self.getOption('tmax_src')
        flag_detrending=self.getOption('flag_detrending')
        flag_dir=self.getOption('sourcename')
        flag_N_RM=self.getOption('flag_N_RM')
        indexfile=self.getOption('indexfile')
        
        # Agilepy works with MJD and TT. RM_LC.py with TT and UTC.
        # Convert MJD to TT
        if self.getOption("timetype") == "MJD":
            T0 = AstroUtils.time_mjd_to_agile_seconds(self.getOption("T0"))
            self.setOptions(T0=T0, timetype='TT')
        
        # TODO: add the following script to Agilepy and make it importable as a module.
        #cmd+= f" {path_script}/RM_LC.py {T0} {tmin} {tmax} {tmax_bkg} {tmax_bkg} {tmin_src} {tmax_src} {flag_detrending} {flag_dir} {flag_N_RM}"
        
        # Move to output directory and run command from there.
        print(f"\nNow Run Script from {self.outdir}\n")
        #os.system(f"echo {indexfile} ")
        #os.chdir(self.outdir)
        #os.system(cmd)
        
        return True

