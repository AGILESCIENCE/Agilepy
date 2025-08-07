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
    
    
    def read_ratemeters(self):
        """
        Run ratemeters scripts.
        """
        self.logger.info("Running ratemeters script")
        
        # Get the value of the parameters for the script
        T0=self.getOption('T0')
        
        # Agilepy works with MJD and TT. RM_LC.py with TT and UTC.
        # Convert MJD to TT
        if self.getOption("timetype") == "MJD":
            T0 = AstroUtils.time_mjd_to_agile_seconds(self.getOption("T0"))
            self.setOptions(T0=T0, timetype='TT')

        return self.read_r(
                        self.getOption('contact'),
                        str(T0),
                        self.getOption('tmin'),
                        self.getOption('tmax'),
                        self.getOption('tmin_bkg'),
                        self.getOption('tmax_bkg'),
                        self.getOption('tmin_src'),
                        self.getOption('tmax_src'),
                        self.getOption('flag_detrending'),
                        self.getOption('sourcename'),
                        self.getOption('flag_N_RM'),
                        # self.getOption('indexfile')            
                )


    def read_r(self, CONT: str, TEMPO: str, SX: float, DX: float, BKG_SX: float, BKG_DX: float, GRB_SX: float, GRB_DX: float, FLAG: str, NAME: str, FLAG_PLOT: str):

        ################
        # A. Ursi 2022 #
        ############################################################################################################################################################################################################################
        # >>> python $GRB/RM_LC.py [contact] [T0 in UTC or OBT] [START] [STOP] [BKG START] [BKG STOP] [GRB START] [GRB STOP] ["ND" or "D" for NON-DETRENDED or DETRENDED] [NAME] ["8RM" or "3RM" for 8 ratemeters or 3 ratemeters] #
        ############################################################################################################################################################################################################################
        # es: python $GRB/RM_LC.py 080686 2022-10-28T13:16:27 -100 100 -100 -90 -1 3 ND GRB221028A 8RM                                                                                                                             #
        ############################################################################################################################################################################################################################

        import os, sys, math, os.path
        import numpy as np
        import matplotlib as mpl
        mpl.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        import time
        from calendar import timegm
        import datetime
        import scipy.fftpack
        from scipy.fftpack import rfft, irfft, fftfreq, fft
        from astropy.io import fits

        ###################
        # INPUT VARIABLES #
        ###################

        if len(TEMPO.split(".")) == 2:
            DECIMALS = float("0.%s" % TEMPO.split(".")[1])
            INTEGERS = str(TEMPO.split(".")[0])
        else:
            DECIMALS = 0
            INTEGERS = TEMPO
        if int(len(INTEGERS)) == 19:
                TTIME = timegm(time.strptime(INTEGERS, '%Y-%m-%dT%H:%M:%S')) - 1072915200 + DECIMALS
        else:
                TTIME = float(INTEGERS) + DECIMALS

 

        UTC = str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(TTIME+1072915200)))
        UT = "%s%s%s" % (UTC[2:4], UTC[5:7], UTC[8:10])

        ####################################
        # READ AND PROCESS 3913 FITS FILES #
        ####################################

        if os.path.isfile("%s_RM/%s_RM-SA_LC.txt" % (NAME, CONT)) == True:
            print("Files exist")

        if os.path.isfile("%s_RM/%s_RM-SA_LC.txt" % (NAME, CONT)) == False:

            print("Converting 3913 files...")

            os.system("mkdir %s_RM" % NAME)

            hdulist = fits.open("/ASDC_PROC2/DATA_2/COR/PKP%s_1_3913_000.lv1.cor.gz" % CONT)
            tbdata = hdulist[1].data

            GRID_1X = []
            GRID_2X = []
            GRID_3X = []
            GRID_4X = []
            GRID_5X = []
            GRID_6X = []
            GRID_1Z = []
            GRID_2Z = []
            GRID_3Z = []
            GRID_4Z = []
            GRID_5Z = []
            GRID_6Z = []

            AC_SIDE0 = []
            AC_SIDE1 = []
            AC_SIDE2 = []
            AC_SIDE3 = []
            AC_SIDE4 = []

            MCAL_X_CH01 = []
            MCAL_X_CH02 = []
            MCAL_X_CH03 = []
            MCAL_X_CH04 = []
            MCAL_X_CH05 = []
            MCAL_X_CH06 = []
            MCAL_X_CH07 = []
            MCAL_X_CH08 = []
            MCAL_X_CH09 = []
            MCAL_X_CH10 = []
            MCAL_X_CH11 = []

            MCAL_Z_CH01 = []
            MCAL_Z_CH02 = []
            MCAL_Z_CH03 = []
            MCAL_Z_CH04 = []
            MCAL_Z_CH05 = []
            MCAL_Z_CH06 = []
            MCAL_Z_CH07 = []
            MCAL_Z_CH08 = []
            MCAL_Z_CH09 = []
            MCAL_Z_CH10 = []
            MCAL_Z_CH11 = []

            SA_DET1_LAD1_CH1 = []
            SA_DET1_LAD1_CH2 = []
            SA_DET1_LAD1_CH3 = []
            SA_DET1_LAD2_CH1 = []
            SA_DET1_LAD2_CH2 = []
            SA_DET1_LAD2_CH3 = []
            SA_DET2_LAD1_CH1 = []
            SA_DET2_LAD1_CH2 = []
            SA_DET2_LAD1_CH3 = []
            SA_DET2_LAD2_CH1 = []
            SA_DET2_LAD2_CH2 = []
            SA_DET2_LAD2_CH3 = []
            SA_DET3_LAD1_CH1 = []
            SA_DET3_LAD1_CH2 = []
            SA_DET3_LAD1_CH3 = []
            SA_DET3_LAD2_CH1 = []
            SA_DET3_LAD2_CH2 = []
            SA_DET3_LAD2_CH3 = []
            SA_DET4_LAD1_CH1 = []
            SA_DET4_LAD1_CH2 = []
            SA_DET4_LAD1_CH3 = []
            SA_DET4_LAD2_CH1 = []
            SA_DET4_LAD2_CH2 = []
            SA_DET4_LAD2_CH3 = []

            TEMPO = []

            for i in range(0,int(tbdata.shape[0])):

                TEMPO.append(float(tbdata[i][19]))

                ###################
                # SILICON TRACKER #
                ###################

                GRID_1X.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][25])])
                GRID_1X.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][37])])
                GRID_1X.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][49])])
                GRID_1X.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][61])])
                GRID_1X.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][73])])
                GRID_1X.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][85])])
                GRID_1X.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][97])])
                GRID_1X.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][109])])

                GRID_2X.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][26])])
                GRID_2X.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][38])])
                GRID_2X.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][50])])
                GRID_2X.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][62])])
                GRID_2X.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][74])])
                GRID_2X.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][86])])
                GRID_2X.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][98])])
                GRID_2X.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][110])])

                GRID_3X.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][27])])
                GRID_3X.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][39])])
                GRID_3X.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][51])])
                GRID_3X.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][63])])
                GRID_3X.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][75])])
                GRID_3X.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][87])])
                GRID_3X.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][99])])
                GRID_3X.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][111])])

                GRID_4X.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][28])])
                GRID_4X.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][40])])
                GRID_4X.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][52])])
                GRID_4X.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][64])])
                GRID_4X.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][76])])
                GRID_4X.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][88])])
                GRID_4X.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][100])])
                GRID_4X.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][112])])

                GRID_5X.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][29])])
                GRID_5X.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][41])])
                GRID_5X.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][53])])
                GRID_5X.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][65])])
                GRID_5X.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][77])])
                GRID_5X.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][89])])
                GRID_5X.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][101])])
                GRID_5X.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][113])])

                GRID_6X.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][30])])
                GRID_6X.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][42])])
                GRID_6X.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][54])])
                GRID_6X.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][66])])
                GRID_6X.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][78])])
                GRID_6X.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][90])])
                GRID_6X.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][102])])
                GRID_6X.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][114])])

                GRID_1Z.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][31])])
                GRID_1Z.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][43])])
                GRID_1Z.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][55])])
                GRID_1Z.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][67])])
                GRID_1Z.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][79])])
                GRID_1Z.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][91])])
                GRID_1Z.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][103])])
                GRID_1Z.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][115])])

                GRID_2Z.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][32])])
                GRID_2Z.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][44])])
                GRID_2Z.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][56])])
                GRID_2Z.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][68])])
                GRID_2Z.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][80])])
                GRID_2Z.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][92])])
                GRID_2Z.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][104])])
                GRID_2Z.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][116])])

                GRID_3Z.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][33])])
                GRID_3Z.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][45])])
                GRID_3Z.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][57])])
                GRID_3Z.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][69])])
                GRID_3Z.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][81])])
                GRID_3Z.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][93])])
                GRID_3Z.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][105])])
                GRID_3Z.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][117])])

                GRID_4Z.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][34])])
                GRID_4Z.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][46])])
                GRID_4Z.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][58])])
                GRID_4Z.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][70])])
                GRID_4Z.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][82])])
                GRID_4Z.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][94])])
                GRID_4Z.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][106])])
                GRID_4Z.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][118])])

                GRID_5Z.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][35])])
                GRID_5Z.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][47])])
                GRID_5Z.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][59])])
                GRID_5Z.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][71])])
                GRID_5Z.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][83])])
                GRID_5Z.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][95])])
                GRID_5Z.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][107])])
                GRID_5Z.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][119])])

                GRID_6Z.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][36])])
                GRID_6Z.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][48])])
                GRID_6Z.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][60])])
                GRID_6Z.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][72])])
                GRID_6Z.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][84])])
                GRID_6Z.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][96])])
                GRID_6Z.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][108])])
                GRID_6Z.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][120])])

                ####################
                # ANTI-COINCIDENCE #
                ####################

                AC_SIDE0.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][121])])
                AC_SIDE0.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][126])])
                AC_SIDE0.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][131])])
                AC_SIDE0.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][136])])
                AC_SIDE0.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][141])])
                AC_SIDE0.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][146])])
                AC_SIDE0.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][151])])
                AC_SIDE0.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][156])])

                AC_SIDE1.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][122])])
                AC_SIDE1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][127])])
                AC_SIDE1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][132])])
                AC_SIDE1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][137])])
                AC_SIDE1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][142])])
                AC_SIDE1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][147])])
                AC_SIDE1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][152])])
                AC_SIDE1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][157])])

                AC_SIDE2.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][123])])
                AC_SIDE2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][128])])
                AC_SIDE2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][133])])
                AC_SIDE2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][138])])
                AC_SIDE2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][143])])
                AC_SIDE2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][148])])
                AC_SIDE2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][153])])
                AC_SIDE2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][158])])

                AC_SIDE3.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][124])])
                AC_SIDE3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][129])])
                AC_SIDE3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][134])])
                AC_SIDE3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][139])])
                AC_SIDE3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][144])])
                AC_SIDE3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][149])])
                AC_SIDE3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][154])])
                AC_SIDE3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][159])])

                AC_SIDE4.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][125])])
                AC_SIDE4.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][130])])
                AC_SIDE4.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][135])])
                AC_SIDE4.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][140])])
                AC_SIDE4.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][145])])
                AC_SIDE4.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][150])])
                AC_SIDE4.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][155])])
                AC_SIDE4.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][160])])

                ####################
                # MINI-CALORIMETER #
                ####################

                MCAL_X_CH01.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][161])])
                MCAL_X_CH01.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][183])])
                MCAL_X_CH01.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][205])])
                MCAL_X_CH01.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][227])])
                MCAL_X_CH01.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][249])])
                MCAL_X_CH01.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][271])])
                MCAL_X_CH01.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][293])])
                MCAL_X_CH01.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][315])])

                MCAL_X_CH02.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][162])])
                MCAL_X_CH02.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][184])])
                MCAL_X_CH02.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][206])])
                MCAL_X_CH02.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][228])])
                MCAL_X_CH02.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][250])])
                MCAL_X_CH02.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][272])])
                MCAL_X_CH02.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][294])])
                MCAL_X_CH02.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][316])])

                MCAL_X_CH03.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][163])])
                MCAL_X_CH03.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][185])])
                MCAL_X_CH03.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][207])])
                MCAL_X_CH03.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][229])])
                MCAL_X_CH03.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][251])])
                MCAL_X_CH03.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][273])])
                MCAL_X_CH03.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][295])])
                MCAL_X_CH03.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][317])])

                MCAL_X_CH04.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][164])])
                MCAL_X_CH04.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][186])])
                MCAL_X_CH04.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][208])])
                MCAL_X_CH04.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][230])])
                MCAL_X_CH04.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][252])])
                MCAL_X_CH04.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][274])])
                MCAL_X_CH04.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][296])])
                MCAL_X_CH04.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][318])])

                MCAL_X_CH05.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][165])])
                MCAL_X_CH05.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][187])])
                MCAL_X_CH05.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][209])])
                MCAL_X_CH05.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][231])])
                MCAL_X_CH05.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][253])])
                MCAL_X_CH05.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][275])])
                MCAL_X_CH05.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][297])])
                MCAL_X_CH05.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][319])])

                MCAL_X_CH06.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][166])])
                MCAL_X_CH06.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][188])])
                MCAL_X_CH06.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][210])])
                MCAL_X_CH06.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][232])])
                MCAL_X_CH06.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][254])])
                MCAL_X_CH06.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][276])])
                MCAL_X_CH06.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][298])])
                MCAL_X_CH06.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][320])])

                MCAL_X_CH07.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][167])])
                MCAL_X_CH07.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][189])])
                MCAL_X_CH07.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][211])])
                MCAL_X_CH07.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][233])])
                MCAL_X_CH07.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][255])])
                MCAL_X_CH07.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][277])])
                MCAL_X_CH07.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][299])])
                MCAL_X_CH07.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][321])])

                MCAL_X_CH08.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][168])])
                MCAL_X_CH08.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][190])])
                MCAL_X_CH08.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][212])])
                MCAL_X_CH08.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][234])])
                MCAL_X_CH08.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][256])])
                MCAL_X_CH08.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][278])])
                MCAL_X_CH08.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][300])])
                MCAL_X_CH08.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][322])])

                MCAL_X_CH09.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][169])])
                MCAL_X_CH09.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][191])])
                MCAL_X_CH09.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][213])])
                MCAL_X_CH09.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][235])])
                MCAL_X_CH09.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][257])])
                MCAL_X_CH09.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][279])])
                MCAL_X_CH09.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][301])])
                MCAL_X_CH09.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][323])])

                MCAL_X_CH10.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][170])])
                MCAL_X_CH10.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][192])])
                MCAL_X_CH10.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][214])])
                MCAL_X_CH10.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][236])])
                MCAL_X_CH10.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][258])])
                MCAL_X_CH10.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][280])])
                MCAL_X_CH10.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][302])])
                MCAL_X_CH10.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][324])])

                MCAL_X_CH11.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][171])])
                MCAL_X_CH11.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][193])])
                MCAL_X_CH11.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][215])])
                MCAL_X_CH11.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][237])])
                MCAL_X_CH11.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][259])])
                MCAL_X_CH11.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][281])])
                MCAL_X_CH11.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][303])])
                MCAL_X_CH11.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][325])])


                MCAL_Z_CH01.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][172])])
                MCAL_Z_CH01.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][194])])
                MCAL_Z_CH01.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][216])])
                MCAL_Z_CH01.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][238])])
                MCAL_Z_CH01.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][260])])
                MCAL_Z_CH01.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][282])])
                MCAL_Z_CH01.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][304])])
                MCAL_Z_CH01.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][326])])

                MCAL_Z_CH02.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][173])])
                MCAL_Z_CH02.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][195])])
                MCAL_Z_CH02.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][217])])
                MCAL_Z_CH02.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][239])])
                MCAL_Z_CH02.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][261])])
                MCAL_Z_CH02.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][283])])
                MCAL_Z_CH02.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][305])])
                MCAL_Z_CH02.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][327])])

                MCAL_Z_CH03.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][174])])
                MCAL_Z_CH03.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][196])])
                MCAL_Z_CH03.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][218])])
                MCAL_Z_CH03.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][240])])
                MCAL_Z_CH03.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][262])])
                MCAL_Z_CH03.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][284])])
                MCAL_Z_CH03.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][306])])
                MCAL_Z_CH03.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][328])])

                MCAL_Z_CH04.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][175])])
                MCAL_Z_CH04.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][197])])
                MCAL_Z_CH04.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][219])])
                MCAL_Z_CH04.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][241])])
                MCAL_Z_CH04.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][262])])
                MCAL_Z_CH04.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][285])])
                MCAL_Z_CH04.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][307])])
                MCAL_Z_CH04.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][329])])

                MCAL_Z_CH05.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][176])])
                MCAL_Z_CH05.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][198])])
                MCAL_Z_CH05.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][220])])
                MCAL_Z_CH05.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][242])])
                MCAL_Z_CH05.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][264])])
                MCAL_Z_CH05.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][286])])
                MCAL_Z_CH05.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][308])])
                MCAL_Z_CH05.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][330])])

                MCAL_Z_CH06.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][177])])
                MCAL_Z_CH06.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][199])])
                MCAL_Z_CH06.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][221])])
                MCAL_Z_CH06.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][243])])
                MCAL_Z_CH06.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][265])])
                MCAL_Z_CH06.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][287])])
                MCAL_Z_CH06.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][309])])
                MCAL_Z_CH06.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][331])])

                MCAL_Z_CH07.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][178])])
                MCAL_Z_CH07.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][200])])
                MCAL_Z_CH07.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][222])])
                MCAL_Z_CH07.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][244])])
                MCAL_Z_CH07.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][266])])
                MCAL_Z_CH07.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][288])])
                MCAL_Z_CH07.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][310])])
                MCAL_Z_CH07.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][332])])

                MCAL_Z_CH08.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][179])])
                MCAL_Z_CH08.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][201])])
                MCAL_Z_CH08.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][223])])
                MCAL_Z_CH08.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][245])])
                MCAL_Z_CH08.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][267])])
                MCAL_Z_CH08.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][289])])
                MCAL_Z_CH08.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][311])])
                MCAL_Z_CH08.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][333])])

                MCAL_Z_CH09.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][180])])
                MCAL_Z_CH09.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][202])])
                MCAL_Z_CH09.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][224])])
                MCAL_Z_CH09.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][246])])
                MCAL_Z_CH09.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][268])])
                MCAL_Z_CH09.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][290])])
                MCAL_Z_CH09.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][312])])
                MCAL_Z_CH09.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][334])])

                MCAL_Z_CH10.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][181])])
                MCAL_Z_CH10.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][203])])
                MCAL_Z_CH10.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][225])])
                MCAL_Z_CH10.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][247])])
                MCAL_Z_CH10.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][269])])
                MCAL_Z_CH10.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][291])])
                MCAL_Z_CH10.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][313])])
                MCAL_Z_CH10.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][335])])

                MCAL_Z_CH11.append([float(tbdata[i][19])+0-8.196, int(tbdata[i][182])])
                MCAL_Z_CH11.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][204])])
                MCAL_Z_CH11.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][226])])
                MCAL_Z_CH11.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][248])])
                MCAL_Z_CH11.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][270])])
                MCAL_Z_CH11.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][292])])
                MCAL_Z_CH11.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][314])])
                MCAL_Z_CH11.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][336])])

                ###############
                # SUPER-AGILE #
                ###############

                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][337])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][361])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][385])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][409])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][433])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][457])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][481])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][505])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][529])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][553])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][577])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][601])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][625])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][649])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][673])])
                SA_DET1_LAD1_CH1.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][697])])

                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][338])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][362])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][386])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][410])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][434])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][458])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][482])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][506])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][530])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][554])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][578])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][602])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][626])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][650])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][674])])
                SA_DET1_LAD1_CH2.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][698])])

                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][339])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][363])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][387])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][411])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][435])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][459])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][483])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][507])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][531])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][555])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][579])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][603])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][627])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][651])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][675])])
                SA_DET1_LAD1_CH3.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][699])])

                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][340])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][364])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][388])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][412])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][436])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][460])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][484])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][508])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][532])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][556])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][580])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][604])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][628])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][652])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][676])])
                SA_DET1_LAD2_CH1.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][700])])

                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][341])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][365])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][389])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][413])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][437])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][461])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][485])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][509])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][533])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][557])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][581])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][605])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][629])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][653])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][677])])
                SA_DET1_LAD2_CH2.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][701])])

                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][342])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][366])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][390])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][414])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][438])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][462])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][486])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][510])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][534])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][558])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][582])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][606])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][630])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][654])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][678])])
                SA_DET1_LAD2_CH3.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][702])])

                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][343])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][367])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][391])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][415])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][439])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][463])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][487])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][511])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][535])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][559])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][583])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][607])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][631])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][655])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][679])])
                SA_DET2_LAD1_CH1.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][703])])

                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][344])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][368])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][392])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][416])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][440])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][464])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][488])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][512])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][536])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][560])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][584])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][608])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][632])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][656])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][680])])
                SA_DET2_LAD1_CH2.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][704])])

                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][345])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][369])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][393])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][417])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][441])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][465])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][489])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][513])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][537])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][561])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][585])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][609])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][633])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][657])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][681])])
                SA_DET2_LAD1_CH3.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][705])])

                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][346])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][370])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][394])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][418])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][442])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][466])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][490])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][514])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][538])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][562])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][586])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][610])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][634])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][658])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][682])])
                SA_DET2_LAD2_CH1.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][706])])

                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][347])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][371])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][395])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][419])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][443])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][467])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][491])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][515])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][539])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][563])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][587])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][611])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][635])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][659])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][683])])
                SA_DET2_LAD2_CH2.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][707])])

                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][348])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][372])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][396])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][420])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][444])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][468])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][492])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][516])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][540])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][564])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][588])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][612])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][636])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][660])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][684])])
                SA_DET2_LAD2_CH3.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][708])])

                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][349])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][373])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][397])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][421])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][445])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][469])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][493])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][517])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][541])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][565])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][589])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][613])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][637])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][661])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][685])])
                SA_DET3_LAD1_CH1.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][709])])

                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][350])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][374])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][398])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][422])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][446])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][470])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][494])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][518])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][542])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][566])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][590])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][614])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][638])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][662])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][686])])
                SA_DET3_LAD1_CH2.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][710])])

                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][351])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][375])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][399])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][423])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][447])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][471])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][495])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][519])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][543])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][567])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][591])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][615])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][639])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][663])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][687])])
                SA_DET3_LAD1_CH3.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][711])])

                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][352])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][376])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][400])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][424])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][448])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][472])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][496])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][520])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][544])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][568])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][592])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][616])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][640])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][664])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][688])])
                SA_DET3_LAD2_CH1.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][712])])

                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][353])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][377])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][401])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][425])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][449])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][473])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][497])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][521])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][545])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][569])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][593])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][617])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][641])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][665])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][689])])
                SA_DET3_LAD2_CH2.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][713])])

                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][354])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][378])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][402])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][426])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][450])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][474])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][498])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][522])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][546])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][570])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][594])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][618])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][642])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][666])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][690])])
                SA_DET3_LAD2_CH3.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][714])])

                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][355])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][379])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][403])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][427])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][451])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][475])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][499])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][523])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][547])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][571])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][595])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][619])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][643])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][667])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][691])])
                SA_DET4_LAD1_CH1.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][715])])

                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][356])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][380])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][404])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][428])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][452])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][476])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][500])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][524])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][548])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][572])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][596])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][620])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][644])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][668])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][692])])
                SA_DET4_LAD1_CH2.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][716])])

                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][357])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][381])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][405])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][429])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][453])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][477])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][501])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][525])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][549])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][573])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][597])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][621])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][645])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][669])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][693])])
                SA_DET4_LAD1_CH3.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][717])])

                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][358])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][382])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][406])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][430])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][454])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][478])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][502])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][526])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][550])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][574])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][598])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][622])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][646])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][670])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][694])])
                SA_DET4_LAD2_CH1.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][718])])

                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][359])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][383])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][407])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][431])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][455])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][479])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][503])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][527])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][551])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][575])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][599])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][623])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][647])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][671])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][695])])
                SA_DET4_LAD2_CH2.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][719])])

                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+0.0-8.196, int(tbdata[i][360])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+0.512-8.196, int(tbdata[i][384])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+1.024-8.196, int(tbdata[i][408])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+1.536-8.196, int(tbdata[i][432])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+2.048-8.196, int(tbdata[i][456])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+2.560-8.196, int(tbdata[i][480])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+3.072-8.196, int(tbdata[i][504])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+3.584-8.196, int(tbdata[i][528])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+4.096-8.196, int(tbdata[i][552])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+4.608-8.196, int(tbdata[i][576])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+5.120-8.196, int(tbdata[i][600])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+5.632-8.196, int(tbdata[i][624])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+6.144-8.196, int(tbdata[i][648])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+6.656-8.196, int(tbdata[i][672])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+7.168-8.196, int(tbdata[i][696])])
                SA_DET4_LAD2_CH3.append([float(tbdata[i][19])+7.680-8.196, int(tbdata[i][720])])

            hdulist.close()

            ####################################
            # CREATE ARRAY FOR SILICON TRACKER #
            ####################################

            GRID = []
            for j in range(len(GRID_1X)):
                GRID.append([GRID_1X[j][0], GRID_1X[j][1]+GRID_2X[j][1]+GRID_3X[j][1]+GRID_4X[j][1]+GRID_5X[j][1]+GRID_6X[j][1]+GRID_1Z[j][1]+GRID_2Z[j][1]+GRID_3Z[j][1]+GRID_4Z[j][1]+GRID_5Z[j][1]+GRID_6Z[j][1]])
            GRID = np.array(GRID)

            #######################################
            # CREATE ARRAYS FOR ANTI-COINCIDENCES #
            #######################################

            AC_SIDE0 = np.array(AC_SIDE0)
            AC_SIDE1 = np.array(AC_SIDE1)
            AC_SIDE2 = np.array(AC_SIDE2)
            AC_SIDE3 = np.array(AC_SIDE3)
            AC_SIDE4 = np.array(AC_SIDE4)

            #####################################
            # CREATE ARRAY FOR MINI-CALORIMETER #
            #####################################

            MCAL = []
            for j in range(len(MCAL_X_CH01)):
                MCAL.append([MCAL_X_CH01[j][0], MCAL_X_CH01[j][1]+MCAL_X_CH02[j][1]+MCAL_X_CH03[j][1]+MCAL_X_CH04[j][1]+MCAL_X_CH05[j][1]+MCAL_X_CH06[j][1]+MCAL_X_CH07[j][1]+MCAL_X_CH08[j][1]+MCAL_X_CH09[j][1]+MCAL_X_CH10[j][1]+MCAL_X_CH11[j][1]+MCAL_Z_CH01[j][1]+MCAL_Z_CH02[j][1]+MCAL_Z_CH03[j][1]+MCAL_Z_CH04[j][1]+MCAL_Z_CH05[j][1]+MCAL_Z_CH06[j][1]+MCAL_Z_CH07[j][1]+MCAL_Z_CH08[j][1]+MCAL_Z_CH09[j][1]+MCAL_Z_CH10[j][1]+MCAL_Z_CH11[j][1]])
            MCAL = np.array(MCAL)

            ################################
            # CREATE ARRAY FOR SUPER-AGILE #
            ################################

            SA = []
            for j in range(len(SA_DET1_LAD1_CH1)):
                SA.append([SA_DET1_LAD1_CH1[j][0], SA_DET1_LAD1_CH1[j][1]+SA_DET1_LAD1_CH2[j][1]+SA_DET1_LAD1_CH3[j][1]+SA_DET1_LAD2_CH1[j][1]+SA_DET1_LAD2_CH2[j][1]+SA_DET1_LAD2_CH3[j][1]+SA_DET2_LAD1_CH1[j][1]+SA_DET2_LAD1_CH2[j][1]+SA_DET2_LAD1_CH3[j][1]+SA_DET2_LAD2_CH1[j][1]+SA_DET2_LAD2_CH2[j][1]+SA_DET2_LAD2_CH3[j][1]+SA_DET3_LAD1_CH1[j][1]+SA_DET3_LAD1_CH2[j][1]+SA_DET3_LAD1_CH3[j][1]+SA_DET3_LAD2_CH1[j][1]+SA_DET3_LAD2_CH2[j][1]+SA_DET3_LAD2_CH3[j][1]+SA_DET4_LAD1_CH1[j][1]+SA_DET4_LAD1_CH2[j][1]+SA_DET4_LAD1_CH3[j][1]+SA_DET4_LAD2_CH1[j][1]+SA_DET4_LAD2_CH2[j][1]+SA_DET4_LAD2_CH3[j][1]])
            SA = np.array(SA)

            #################################################
            # APPLY FFT DETRENDING OF BACKGROUND MODULATION #
            #################################################

            GRIDxf = np.arange(0.0, int(len(GRID)), 1.0)
            GRIDxf = GRIDxf/float(GRID[len(GRID)-1][0]-GRID[0][0])
            GRIDyf = (2 / np.sum(GRID[:,1])) * abs(scipy.fftpack.fft(GRID[:,1]))**2 #* scipy.fftpack.rfft(y)
            GRIDxf = GRIDxf[:len(GRIDxf)/2]
            GRIDyf = GRIDyf[:len(GRIDyf)/2]
            GRIDf_signal = rfft(GRID[:,1])
            GRIDW = fftfreq(GRID[:,1].size, d=0.512)
            GRIDcut_f_signalsx = GRIDf_signal.copy()
            GRIDcut_f_signaldx = GRIDf_signal.copy()
            GRIDcut_f_signalsx[(GRIDW>1e-4)] = 0
            GRIDcut_f_signaldx[(GRIDW<1e-2)] = 0
            GRIDcut_f_signal = GRIDcut_f_signalsx + GRIDcut_f_signaldx
            GRIDcut_signal = irfft(GRIDcut_f_signal)

            SAxf = np.arange(0.0, int(len(SA)), 1.0)
            SAxf = SAxf/float(SA[len(SA)-1][0]-SA[0][0])
            SAyf = (2 / np.sum(SA[:,1])) * abs(scipy.fftpack.fft(SA[:,1]))**2 #* scipy.fftpack.rfft(y)
            SAxf = SAxf[:len(SAxf)/2]
            SAyf = SAyf[:len(SAyf)/2]
            SAf_signal = rfft(SA[:,1])
            SAW = fftfreq(SA[:,1].size, d=0.512)
            SAcut_f_signalsx = SAf_signal.copy()
            SAcut_f_signaldx = SAf_signal.copy()
            SAcut_f_signalsx[(SAW>1e-4)] = 0
            SAcut_f_signaldx[(SAW<1e-2)] = 0
            SAcut_f_signal = SAcut_f_signalsx + SAcut_f_signaldx
            SAcut_signal = irfft(SAcut_f_signal)

            MCALxf = np.arange(0.0, int(len(MCAL)), 1.0)
            MCALxf = MCALxf/float(MCAL[len(MCAL)-1][0]-MCAL[0][0])
            MCALyf = (2 / np.sum(MCAL[:,1])) * abs(scipy.fftpack.fft(MCAL[:,1]))**2 #* scipy.fftpack.rfft(y)
            MCALxf = MCALxf[:len(MCALxf)/2]
            MCALyf = MCALyf[:len(MCALyf)/2]
            MCALf_signal = rfft(MCAL[:,1])
            MCALW = fftfreq(MCAL[:,1].size, d=1.024)
            MCALcut_f_signalsx = MCALf_signal.copy()
            MCALcut_f_signaldx = MCALf_signal.copy()
            MCALcut_f_signalsx[(MCALW>1e-5)] = 0
            MCALcut_f_signaldx[(MCALW<3e-2)] = 0
            MCALcut_f_signal = MCALcut_f_signalsx + MCALcut_f_signaldx
            MCALcut_signal = irfft(MCALcut_f_signal)

            AC0xf = np.arange(0.0, int(len(AC_SIDE0)), 1.0)
            AC0xf = AC0xf/float(AC_SIDE0[len(AC_SIDE0)-1][0]-AC_SIDE0[0][0])
            AC0yf = (2 / np.sum(AC_SIDE0[:,1])) * abs(scipy.fftpack.fft(AC_SIDE0[:,1]))**2 #* scipy.fftpack.rfft(y)
            AC0xf = AC0xf[:len(AC0xf)/2]
            AC0yf = AC0yf[:len(AC0yf)/2]
            AC0f_signal = rfft(AC_SIDE0[:,1])
            AC0W = fftfreq(AC_SIDE0[:,1].size, d=1.024)
            AC0cut_f_signalsx = AC0f_signal.copy()
            AC0cut_f_signaldx = AC0f_signal.copy()
            AC0cut_f_signalsx[(AC0W>1e-5)] = 0
            AC0cut_f_signaldx[(AC0W<3e-2)] = 0
            AC0cut_f_signal = AC0cut_f_signalsx + AC0cut_f_signaldx
            AC0cut_signal = irfft(AC0cut_f_signal)

            AC1xf = np.arange(0.0, int(len(AC_SIDE1)), 1.0)
            AC1xf = AC1xf/float(AC_SIDE1[len(AC_SIDE1)-1][0]-AC_SIDE1[0][0])
            AC1yf = (2 / np.sum(AC_SIDE1[:,1])) * abs(scipy.fftpack.fft(AC_SIDE1[:,1]))**2 #* scipy.fftpack.rfft(y)
            AC1xf = AC1xf[:len(AC1xf)/2]
            AC1yf = AC1yf[:len(AC1yf)/2]
            AC1f_signal = rfft(AC_SIDE1[:,1])
            AC1W = fftfreq(AC_SIDE1[:,1].size, d=1.024)
            AC1cut_f_signalsx = AC1f_signal.copy()
            AC1cut_f_signaldx = AC1f_signal.copy()
            AC1cut_f_signalsx[(AC1W>1e-5)] = 0
            AC1cut_f_signaldx[(AC1W<3e-2)] = 0
            AC1cut_f_signal = AC1cut_f_signalsx + AC1cut_f_signaldx
            AC1cut_signal = irfft(AC1cut_f_signal)

            AC2xf = np.arange(0.0, int(len(AC_SIDE2)), 1.0)
            AC2xf = AC2xf/float(AC_SIDE2[len(AC_SIDE2)-1][0]-AC_SIDE2[0][0])
            AC2yf = (2 / np.sum(AC_SIDE2[:,1])) * abs(scipy.fftpack.fft(AC_SIDE2[:,1]))**2 #* scipy.fftpack.rfft(y)
            AC2xf = AC2xf[:len(AC2xf)/2]
            AC2yf = AC2yf[:len(AC2yf)/2]
            AC2f_signal = rfft(AC_SIDE2[:,1])
            AC2W = fftfreq(AC_SIDE2[:,1].size, d=1.024)
            AC2cut_f_signalsx = AC2f_signal.copy()
            AC2cut_f_signaldx = AC2f_signal.copy()
            AC2cut_f_signalsx[(AC2W>1e-5)] = 0
            AC2cut_f_signaldx[(AC2W<3e-2)] = 0
            AC2cut_f_signal = AC2cut_f_signalsx + AC2cut_f_signaldx
            AC2cut_signal = irfft(AC2cut_f_signal)

            AC3xf = np.arange(0.0, int(len(AC_SIDE3)), 1.0)
            AC3xf = AC3xf/float(AC_SIDE3[len(AC_SIDE3)-1][0]-AC_SIDE3[0][0])
            AC3yf = (2 / np.sum(AC_SIDE3[:,1])) * abs(scipy.fftpack.fft(AC_SIDE3[:,1]))**2 #* scipy.fftpack.rfft(y)
            AC3xf = AC3xf[:len(AC3xf)/2]
            AC3yf = AC3yf[:len(AC3yf)/2]
            AC3f_signal = rfft(AC_SIDE3[:,1])
            AC3W = fftfreq(AC_SIDE3[:,1].size, d=1.024)
            AC3cut_f_signalsx = AC3f_signal.copy()
            AC3cut_f_signaldx = AC3f_signal.copy()
            AC3cut_f_signalsx[(AC3W>1e-5)] = 0
            AC3cut_f_signaldx[(AC3W<3e-2)] = 0
            AC3cut_f_signal = AC3cut_f_signalsx + AC3cut_f_signaldx
            AC3cut_signal = irfft(AC3cut_f_signal)

            AC4xf = np.arange(0.0, int(len(AC_SIDE4)), 1.0)
            AC4xf = AC4xf/float(AC_SIDE4[len(AC_SIDE4)-1][0]-AC_SIDE4[0][0])
            AC4yf = (2 / np.sum(AC_SIDE4[:,1])) * abs(scipy.fftpack.fft(AC_SIDE4[:,1]))**2 #* scipy.fftpack.rfft(y)
            AC4xf = AC4xf[:len(AC4xf)/2]
            AC4yf = AC4yf[:len(AC4yf)/2]
            AC4f_signal = rfft(AC_SIDE4[:,1])
            AC4W = fftfreq(AC_SIDE4[:,1].size, d=1.024)
            AC4cut_f_signalsx = AC4f_signal.copy()
            AC4cut_f_signaldx = AC4f_signal.copy()
            AC4cut_f_signalsx[(AC4W>1e-5)] = 0
            AC4cut_f_signaldx[(AC4W<3e-2)] = 0
            AC4cut_f_signal = AC4cut_f_signalsx + AC4cut_f_signaldx
            AC4cut_signal = irfft(AC4cut_f_signal)

            ###########################
            # CREATE RATEMETERS FILES #
            ###########################

            f_GRID = open("%s_RM/%s_RM-GRID_LC.txt" % (NAME, CONT), "w")
            for p in range(len(GRID)):
                f_GRID.write("OBT %f\tCOUNTS %f\tCOUNTS_D %f\n" % (GRID[p][0], GRID[p][1], GRIDcut_signal[p]))
            f_GRID.close()

            f_SA = open("%s_RM/%s_RM-SA_LC.txt" % (NAME, CONT), "w")
            for p in range(len(SA)):
                f_SA.write("OBT %f\tCOUNTS %f\tCOUNTS_D %f\n" % (SA[p][0], SA[p][1], SAcut_signal[p]))
            f_SA.close()

            f_MCAL = open("%s_RM/%s_RM-MCAL_LC.txt" % (NAME, CONT), "w")
            for p in range(len(MCAL)):
                f_MCAL.write("OBT %f\tCOUNTS %f\tCOUNTS_D %f\n" % (MCAL[p][0], MCAL[p][1], MCALcut_signal[p]))
            f_MCAL.close()

            f_AC0 = open("%s_RM/%s_RM-AC0_LC.txt" % (NAME, CONT), "w")
            for p in range(int(len(AC_SIDE0))):
                f_AC0.write("OBT %f\tCOUNTS %f\tCOUNTS_D %f\n" % (AC_SIDE0[p][0], AC_SIDE0[p][1], AC0cut_signal[p]))
            f_AC0.close()

            f_AC1 = open("%s_RM/%s_RM-AC1_LC.txt" % (NAME, CONT), "w")
            for p in range(int(len(AC_SIDE1))):
                f_AC1.write("OBT %f\tCOUNTS %f\tCOUNTS_D %f\n" % (AC_SIDE1[p][0], AC_SIDE1[p][1], AC1cut_signal[p]))
            f_AC1.close()

            f_AC2 = open("%s_RM/%s_RM-AC2_LC.txt" % (NAME, CONT), "w")
            for p in range(int(len(AC_SIDE2))):
                f_AC2.write("OBT %f\tCOUNTS %f\tCOUNTS_D %f\n" % (AC_SIDE2[p][0], AC_SIDE2[p][1], AC2cut_signal[p]))
            f_AC2.close()

            f_AC3 = open("%s_RM/%s_RM-AC3_LC.txt" % (NAME, CONT), "w")
            for p in range(int(len(AC_SIDE3))):
                f_AC3.write("OBT %f\tCOUNTS %f\tCOUNTS_D %f\n" % (AC_SIDE3[p][0], AC_SIDE3[p][1], AC3cut_signal[p]))
            f_AC3.close()

            f_AC4 = open("%s_RM/%s_RM-AC4_LC.txt" % (NAME, CONT), "w")
            for p in range(int(len(AC_SIDE4))):
                f_AC4.write("OBT %f\tCOUNTS %f\tCOUNTS_D %f\n" % (AC_SIDE4[p][0], AC_SIDE4[p][1], AC4cut_signal[p]))
            f_AC4.close()

        ###############################################
        # READ AND CREATE SuperAGILE RMs LIGHT CURVES #
        ###############################################

        SA = []
        GRB_SA = []
        BKG_SA = []
        GRB_SA_DET = []
        BKG_SA_DET = []
        f_SA = open("%s_RM/%s_RM-SA_LC.txt" % (NAME, CONT), "r")
        for line_SA in f_SA:
            line_SA = line_SA.strip()
            col_SA = line_SA.split()
            SA.append([float(col_SA[1]), float(col_SA[3]), float(col_SA[5])])
            if (float(col_SA[1])-TTIME) >= BKG_SX and (float(col_SA[1])-TTIME) <= BKG_DX:
                BKG_SA.append(float(col_SA[3]))
                BKG_SA_DET.append(float(col_SA[5]))
            if (float(col_SA[1])-TTIME) >= GRB_SX and (float(col_SA[1])-TTIME) <= GRB_DX:
                GRB_SA.append(float(col_SA[3]))
                GRB_SA_DET.append(float(col_SA[5]))
        f_SA.close()
        SA = np.array(SA)
        BKG_SA = np.array(BKG_SA)
        GRB_SA = np.array(GRB_SA)
        BKG_SA_DET = np.array(BKG_SA_DET)
        GRB_SA_DET = np.array(GRB_SA_DET)

        #REB = 3
        #SA_reb = []
        #for i in range(REB-1,int(float(len(SA)/REB))-1):
        #    SA_reb.append([float(SA[REB*i][0]-(1/REB)), np.sum(SA[REB*i-(REB-1):REB*i,1]), np.sum(SA[REB*i-(REB-1):REB*i,2])])
        #SA_reb = np.array(SA_reb)

        #########################################
        # READ AND CREATE MCAL RMs LIGHT CURVES #
        #########################################

        MCAL = []
        GRB_MCAL = []
        BKG_MCAL = []
        GRB_MCAL_DET = []
        BKG_MCAL_DET = []
        f_MCAL = open("%s_RM/%s_RM-MCAL_LC.txt" % (NAME, CONT), "r")
        for line_MCAL in f_MCAL:
            line_MCAL = line_MCAL.strip()
            col_MCAL = line_MCAL.split()
            MCAL.append([float(col_MCAL[1]), float(col_MCAL[3]), float(col_MCAL[5])])
            if (float(col_MCAL[1])-TTIME) >= BKG_SX and (float(col_MCAL[1])-TTIME) <= BKG_DX:
                BKG_MCAL.append(float(col_MCAL[3]))
                BKG_MCAL_DET.append(float(col_MCAL[5]))
            if (float(col_MCAL[1])-TTIME) >= GRB_SX and (float(col_MCAL[1])-TTIME) <= GRB_DX:
                GRB_MCAL.append(float(col_MCAL[3]))
                GRB_MCAL_DET.append(float(col_MCAL[5]))
        f_MCAL.close()
        MCAL = np.array(MCAL)
        BKG_MCAL = np.array(BKG_MCAL)
        GRB_MCAL = np.array(GRB_MCAL)
        BKG_MCAL_DET = np.array(BKG_MCAL_DET)
        GRB_MCAL_DET = np.array(GRB_MCAL_DET)

        #########################################
        # READ AND CREATE GRID RMs LIGHT CURVES #
        #########################################

        GRID = []
        GRB_GRID = []
        BKG_GRID = []
        GRB_GRID_DET = []
        BKG_GRID_DET = []
        f_GRID = open("%s_RM/%s_RM-GRID_LC.txt" % (NAME, CONT), "r")
        for line_GRID in f_GRID:
            line_GRID = line_GRID.strip()
            col_GRID = line_GRID.split()
            GRID.append([float(col_GRID[1]), float(col_GRID[3]), float(col_GRID[5])])
            if (float(col_GRID[1])-TTIME) >= BKG_SX and (float(col_GRID[1])-TTIME) <= BKG_DX:
                BKG_GRID.append(float(col_GRID[3]))
                BKG_GRID_DET.append(float(col_GRID[5]))
            if (float(col_GRID[1])-TTIME) >= GRB_SX and (float(col_GRID[1])-TTIME) <= GRB_DX:
                GRB_GRID.append(float(col_GRID[3]))
                GRB_GRID_DET.append(float(col_GRID[5]))
        f_GRID.close()
        GRID = np.array(GRID)
        BKG_GRID = np.array(BKG_GRID)
        GRB_GRID = np.array(GRB_GRID)
        BKG_GRID_DET = np.array(BKG_GRID_DET)
        GRB_GRID_DET = np.array(GRB_GRID_DET)

        ###########################################
        # READ AND CREATE AC Top RMs LIGHT CURVES #
        ###########################################

        AC0 = []
        GRB_AC0 = []
        BKG_AC0 = []
        GRB_AC0_DET = []
        BKG_AC0_DET = []
        f_AC0 = open("%s_RM/%s_RM-AC0_LC.txt" % (NAME, CONT), "r")
        for line_AC0 in f_AC0:
            line_AC0 = line_AC0.strip()
            col_AC0 = line_AC0.split()
            AC0.append([float(col_AC0[1]), float(col_AC0[3]), float(col_AC0[5])])
            if (float(col_AC0[1])-TTIME) >= BKG_SX and (float(col_AC0[1])-TTIME) <= BKG_DX:
                BKG_AC0.append(float(col_AC0[3]))
                BKG_AC0_DET.append(float(col_AC0[5]))
            if (float(col_AC0[1])-TTIME) >= GRB_SX and (float(col_AC0[1])-TTIME) <= GRB_DX:
                GRB_AC0.append(float(col_AC0[3]))
                GRB_AC0_DET.append(float(col_AC0[5]))
        f_AC0.close()
        AC0 = np.array(AC0)
        BKG_AC0 = np.array(BKG_AC0)
        GRB_AC0 = np.array(GRB_AC0)
        BKG_AC0_DET = np.array(BKG_AC0_DET)
        GRB_AC0_DET = np.array(GRB_AC0_DET)

        #############################################
        # READ AND CREATE AC Lat 1 RMs LIGHT CURVES #
        #############################################

        AC1 = []
        GRB_AC1 = []
        BKG_AC1 = []
        GRB_AC1_DET = []
        BKG_AC1_DET = []
        f_AC1 = open("%s_RM/%s_RM-AC1_LC.txt" % (NAME, CONT), "r")
        for line_AC1 in f_AC1:
            line_AC1 = line_AC1.strip()
            col_AC1 = line_AC1.split()
            AC1.append([float(col_AC1[1]), float(col_AC1[3]), float(col_AC1[5])])
            if (float(col_AC1[1])-TTIME) >= BKG_SX and (float(col_AC1[1])-TTIME) <= BKG_DX:
                BKG_AC1.append(float(col_AC1[3]))
                BKG_AC1_DET.append(float(col_AC1[5]))
            if (float(col_AC1[1])-TTIME) >= GRB_SX and (float(col_AC1[1])-TTIME) <= GRB_DX:
                GRB_AC1.append(float(col_AC1[3]))
                GRB_AC1_DET.append(float(col_AC1[5]))
        f_AC1.close()
        AC1 = np.array(AC1)
        BKG_AC1 = np.array(BKG_AC1)
        GRB_AC1 = np.array(GRB_AC1)
        BKG_AC1_DET = np.array(BKG_AC1_DET)
        GRB_AC1_DET = np.array(GRB_AC1_DET)

        #############################################
        # READ AND CREATE AC Lat 2 RMs LIGHT CURVES #
        #############################################


        AC2 = []
        GRB_AC2 = []
        BKG_AC2 = []
        GRB_AC2_DET = []
        BKG_AC2_DET = []
        f_AC2 = open("%s_RM/%s_RM-AC2_LC.txt" % (NAME, CONT), "r")
        for line_AC2 in f_AC2:
            line_AC2 = line_AC2.strip()
            col_AC2 = line_AC2.split()
            AC2.append([float(col_AC2[1]), float(col_AC2[3]), float(col_AC2[5])])
            if (float(col_AC2[1])-TTIME) >= BKG_SX and (float(col_AC2[1])-TTIME) <= BKG_DX:
                BKG_AC2.append(float(col_AC2[3]))
                BKG_AC2_DET.append(float(col_AC2[5]))
            if (float(col_AC2[1])-TTIME) >= GRB_SX and (float(col_AC2[1])-TTIME) <= GRB_DX:
                GRB_AC2.append(float(col_AC2[3]))
                GRB_AC2_DET.append(float(col_AC2[5]))
        f_AC2.close()
        AC2 = np.array(AC2)
        BKG_AC2 = np.array(BKG_AC2)
        GRB_AC2 = np.array(GRB_AC2)
        BKG_AC2_DET = np.array(BKG_AC2_DET)
        GRB_AC2_DET = np.array(GRB_AC2_DET)

        #############################################
        # READ AND CREATE AC Lat 3 RMs LIGHT CURVES #
        #############################################

        AC3 = []
        GRB_AC3 = []
        BKG_AC3 = []
        GRB_AC3_DET = []
        BKG_AC3_DET = []
        f_AC3 = open("%s_RM/%s_RM-AC3_LC.txt" % (NAME, CONT), "r")
        for line_AC3 in f_AC3:
            line_AC3 = line_AC3.strip()
            col_AC3 = line_AC3.split()
            AC3.append([float(col_AC3[1]), float(col_AC3[3]), float(col_AC3[5])])
            if (float(col_AC3[1])-TTIME) >= BKG_SX and (float(col_AC3[1])-TTIME) <= BKG_DX:
                BKG_AC3.append(float(col_AC3[3]))
                BKG_AC3_DET.append(float(col_AC3[5]))
            if (float(col_AC3[1])-TTIME) >= GRB_SX and (float(col_AC3[1])-TTIME) <= GRB_DX:
                GRB_AC3.append(float(col_AC3[3]))
                GRB_AC3_DET.append(float(col_AC3[5]))
        f_AC3.close()
        AC3 = np.array(AC3)
        BKG_AC3 = np.array(BKG_AC3)
        GRB_AC3 = np.array(GRB_AC3)
        BKG_AC3_DET = np.array(BKG_AC3_DET)
        GRB_AC3_DET = np.array(GRB_AC3_DET)

        #############################################
        # READ AND CREATE AC Lat 4 RMs LIGHT CURVES #
        #############################################

        AC4 = []
        GRB_AC4 = []
        BKG_AC4 = []
        GRB_AC4_DET = []
        BKG_AC4_DET = []
        f_AC4 = open("%s_RM/%s_RM-AC4_LC.txt" % (NAME, CONT), "r")
        for line_AC4 in f_AC4:
            line_AC4 = line_AC4.strip()
            col_AC4 = line_AC4.split()
            AC4.append([float(col_AC4[1]), float(col_AC4[3]), float(col_AC4[5])])
            if (float(col_AC4[1])-TTIME) >= BKG_SX and (float(col_AC4[1])-TTIME) <= BKG_DX:
                BKG_AC4.append(float(col_AC4[3]))
                BKG_AC4_DET.append(float(col_AC4[5]))
            if (float(col_AC4[1])-TTIME) >= GRB_SX and (float(col_AC4[1])-TTIME) <= GRB_DX:
                GRB_AC4.append(float(col_AC4[3]))
                GRB_AC4_DET.append(float(col_AC4[5]))
        f_AC4.close()
        AC4 = np.array(AC4)
        BKG_AC4 = np.array(BKG_AC4)
        GRB_AC4 = np.array(GRB_AC4)
        BKG_AC4_DET = np.array(BKG_AC4_DET)
        GRB_AC4_DET = np.array(GRB_AC4_DET)

        ##############################################
        # PRINT NUMBER OF COUNTS AND BACKGROUND RATE #
        ##############################################

        if FLAG == 'ND':

            print("SA:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_SA), 2*np.mean(BKG_SA)))
            print("AC Top:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC0), np.mean(BKG_AC0)))
            print("AC1:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC1), np.mean(BKG_AC1)))
            print("AC2:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC2), np.mean(BKG_AC2)))
            print("AC3:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC3), np.mean(BKG_AC3)))
            print("AC4:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC4), np.mean(BKG_AC4)))
            print("MCAL:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_MCAL), np.mean(BKG_MCAL)))
            print("GRID:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_GRID), np.mean(BKG_GRID)))

        if FLAG == 'D':

            print("SA:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_SA_DET), 2*np.mean(BKG_SA_DET)))
            print("AC Top:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC0_DET), np.mean(BKG_AC0_DET)))
            print("AC1:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC1_DET), np.mean(BKG_AC1_DET)))
            print("AC2:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC2_DET), np.mean(BKG_AC2_DET)))
            print("AC3:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC3_DET), np.mean(BKG_AC3_DET)))
            print("AC4:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_AC4_DET), np.mean(BKG_AC4_DET)))
            print("MCAL:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_MCAL_DET), np.mean(BKG_MCAL_DET)))
            print("GRID:\t%d counts above a background rate of %d Hz" % (np.sum(GRB_GRID_DET), np.mean(BKG_GRID_DET)))

        ##################################################
        # CREATE PLOT WITH RATEMETERS FOR ALL RATEMETERS #
        ##################################################

        if FLAG_PLOT == '8RM':

            fig = plt.figure(figsize=(25,25))

            ax_SA = fig.add_subplot(811)
            ax_SA.set_title('AGILE Scientific Ratemeters\nT0 = %s (UT)\n' % UTC, fontsize=25)
            if FLAG == 'ND': ax_SA.step(SA[:,0]-TTIME, SA[:,1], markersize=5, c='navy', linewidth=1, label='SuperAGILE [18-60 keV]')
            if FLAG == 'D': ax_SA.step(SA[:,0]-TTIME, SA[:,2], markersize=5, c='navy', linewidth=1, label='SuperAGILE [18-60 keV]')
            ax_SA.set_ylabel('SA\n[counts / 0.5 s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_SA.get_xticklabels(), fontsize=18)
            plt.setp(ax_SA.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_SA.set_xlim(SX,DX)
            if FLAG == 'ND': ax_SA.set_ylim(np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]), np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1])-np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_SA.set_ylim(np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]), np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2])-np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_AC0 = fig.add_subplot(812)
            if FLAG == 'ND': ax_AC0.step(AC0[:,0]-TTIME, AC0[:,1], markersize=5, c='green', linewidth=1, label='AC Top [50-200 keV]')
            if FLAG == 'D': ax_AC0.step(AC0[:,0]-TTIME, AC0[:,2], markersize=5, c='green', linewidth=1, label='AC Top [50-200 keV]')
            ax_AC0.set_ylabel('AC TOP\n[counts / s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_AC0.get_xticklabels(), fontsize=18)
            plt.setp(ax_AC0.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_AC0.set_xlim(SX,DX)
            if FLAG == 'ND': ax_AC0.set_ylim(np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1])-np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_AC0.set_ylim(np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2])-np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_AC1 = fig.add_subplot(813)
            if FLAG == 'ND': ax_AC1.step(AC1[:,0]-TTIME, AC1[:,1], markersize=5, c='green', linewidth=1, label='AC Lat 1 [80-200 keV]')
            if FLAG == 'D': ax_AC1.step(AC1[:,0]-TTIME, AC1[:,2], markersize=5, c='green', linewidth=1, label='AC Lat 1 [80-200 keV]')
            ax_AC1.set_ylabel('AC Lat 1\n[counts / s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_AC1.get_xticklabels(), fontsize=18)
            plt.setp(ax_AC1.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_AC1.set_xlim(SX,DX)
            if FLAG == 'ND': ax_AC1.set_ylim(np.min(AC1[np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][0] : np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][len(np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC1[np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][0] : np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][len(np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(AC1[np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][0] : np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][len(np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0])-1], 1])-np.min(AC1[np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][0] : np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][len(np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_AC1.set_ylim(np.min(AC1[np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][0] : np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][len(np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC1[np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][0] : np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][len(np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(AC1[np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][0] : np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][len(np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0])-1], 2])-np.min(AC1[np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][0] : np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0][len(np.where((AC1[:,0]>TTIME+SX)&(AC1[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_AC2 = fig.add_subplot(814)
            if FLAG == 'ND': ax_AC2.step(AC2[:,0]-TTIME, AC2[:,1], markersize=5, c='green', linewidth=1, label='AC Lat 2 [80-200 keV]')
            if FLAG == 'D': ax_AC2.step(AC2[:,0]-TTIME, AC2[:,2], markersize=5, c='green', linewidth=1, label='AC Lat 2 [80-200 keV]')
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            ax_AC2.set_ylabel('AC Lat 2\n[counts / s]', fontsize=20)
            plt.setp(ax_AC2.get_xticklabels(), fontsize=18)
            plt.setp(ax_AC2.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_AC2.set_xlim(SX,DX)
            if FLAG == 'ND': ax_AC2.set_ylim(np.min(AC2[np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][0] : np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][len(np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC2[np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][0] : np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][len(np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(AC2[np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][0] : np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][len(np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0])-1], 1])-np.min(AC2[np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][0] : np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][len(np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_AC2.set_ylim(np.min(AC2[np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][0] : np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][len(np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC2[np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][0] : np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][len(np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(AC2[np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][0] : np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][len(np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0])-1], 2])-np.min(AC2[np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][0] : np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0][len(np.where((AC2[:,0]>TTIME+SX)&(AC2[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_AC3 = fig.add_subplot(815)
            if FLAG == 'ND': ax_AC3.step(AC3[:,0]-TTIME, AC3[:,1], markersize=5, c='green', linewidth=1, label='AC Lat 3 [80-200 keV]')
            if FLAG == 'D': ax_AC3.step(AC3[:,0]-TTIME, AC3[:,2], markersize=5, c='green', linewidth=1, label='AC Lat 3 [80-200 keV]')
            ax_AC3.set_ylabel('AC Lat 3\n[counts / s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_AC3.get_xticklabels(), fontsize=18)
            plt.setp(ax_AC3.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_AC3.set_xlim(SX,DX)
            if FLAG == 'ND': ax_AC3.set_ylim(np.min(AC3[np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][0] : np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][len(np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC3[np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][0] : np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][len(np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(AC3[np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][0] : np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][len(np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0])-1], 1])-np.min(AC3[np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][0] : np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][len(np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_AC3.set_ylim(np.min(AC3[np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][0] : np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][len(np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC3[np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][0] : np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][len(np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(AC3[np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][0] : np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][len(np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0])-1], 2])-np.min(AC3[np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][0] : np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0][len(np.where((AC3[:,0]>TTIME+SX)&(AC3[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_AC4 = fig.add_subplot(816)
            if FLAG == 'ND': ax_AC4.step(AC4[:,0]-TTIME, AC4[:,1], markersize=5, c='green', linewidth=1, label='AC Lat 4 [80-200 keV]')
            if FLAG == 'D': ax_AC4.step(AC4[:,0]-TTIME, AC4[:,2], markersize=5, c='green', linewidth=1, label='AC Lat 4 [80-200 keV]')
            ax_AC4.set_ylabel('AC Lat 4\n[counts / s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_AC4.get_xticklabels(), fontsize=18)
            plt.setp(ax_AC4.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_AC4.set_xlim(SX,DX)
            if FLAG == 'ND': ax_AC4.set_ylim(np.min(AC4[np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][0] : np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][len(np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC4[np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][0] : np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][len(np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(AC4[np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][0] : np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][len(np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0])-1], 1])-np.min(AC4[np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][0] : np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][len(np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_AC4.set_ylim(np.min(AC4[np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][0] : np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][len(np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC4[np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][0] : np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][len(np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(AC4[np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][0] : np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][len(np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0])-1], 2])-np.min(AC4[np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][0] : np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0][len(np.where((AC4[:,0]>TTIME+SX)&(AC4[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_MCAL = fig.add_subplot(817)
            if FLAG == 'ND': ax_MCAL.step(MCAL[:,0]-TTIME, MCAL[:,1], markersize=5, c='red', linewidth=1, label='MCAL [0.4-100 MeV]')
            if FLAG == 'D': ax_MCAL.step(MCAL[:,0]-TTIME, MCAL[:,2], markersize=5, c='red', linewidth=1, label='MCAL [0.4-100 MeV]')
            ax_MCAL.set_ylabel('MCAL\n[counts / s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_MCAL.get_xticklabels(), fontsize=18)
            plt.setp(ax_MCAL.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_MCAL.set_xlim(SX,DX)
            if FLAG == 'ND': ax_MCAL.set_ylim(np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]), np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1])-np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_MCAL.set_ylim(np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]), np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2])-np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_GRID = fig.add_subplot(818)
            if FLAG == 'ND': ax_GRID.step(GRID[:,0]-TTIME, GRID[:,1], markersize=5, c='magenta', linewidth=1, label='GRID [>50 MeV]')
            if FLAG == 'D': ax_GRID.step(GRID[:,0]-TTIME, GRID[:,2], markersize=5, c='magenta', linewidth=1, label='GRID [>50 MeV]')
            ax_GRID.set_ylabel('GRID\n[counts / s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_GRID.get_xticklabels(), fontsize=18)
            plt.setp(ax_GRID.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_GRID.set_xlim(SX,DX)
            if FLAG == 'ND': ax_GRID.set_ylim(np.min(GRID[np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][0] : np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][len(np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0])-1], 1]), np.max(GRID[np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][0] : np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][len(np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(GRID[np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][0] : np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][len(np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0])-1], 1])-np.min(GRID[np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][0] : np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][len(np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_GRID.set_ylim(np.min(GRID[np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][0] : np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][len(np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0])-1], 1]), np.max(GRID[np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][0] : np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][len(np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(GRID[np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][0] : np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][len(np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0])-1], 2])-np.min(GRID[np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][0] : np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0][len(np.where((GRID[:,0]>TTIME+SX)&(GRID[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_GRID.set_xlabel('\nt - T0 [s]', fontsize=25)
            if FLAG == 'ND': plt.savefig("%s_RM/%s_AGILE_RM_ND.png" % (NAME, NAME))
            if FLAG == 'D': plt.savefig("%s_RM/%s_AGILE_RM_D.png" % (NAME, NAME))
            plt.close(fig)

        if FLAG_PLOT == '3RM':

            fig = plt.figure(figsize=(20,14))

            ax_SA = fig.add_subplot(311)
            ax_SA.set_title('AGILE Scientific Ratemeters\nT0 = %s (UT)\n' % UTC, fontsize=25)
            if FLAG == 'ND': ax_SA.step(SA[:,0]-TTIME, SA[:,1], markersize=5, c='navy', linewidth=1, label='SuperAGILE [18-60 keV]')
            if FLAG == 'D': ax_SA.step(SA[:,0]-TTIME, SA[:,2], markersize=5, c='navy', linewidth=1, label='SuperAGILE [18-60 keV]')
            ax_SA.set_ylabel('SA\n[counts / 0.5 s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_SA.get_xticklabels(), fontsize=18)
            plt.setp(ax_SA.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_SA.set_xlim(SX,DX)
            if FLAG == 'ND': ax_SA.set_ylim(np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]), np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1])-np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_SA.set_ylim(np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]), np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2])-np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_AC0 = fig.add_subplot(312)
            if FLAG == 'ND': ax_AC0.step(AC0[:,0]-TTIME, AC0[:,1], markersize=5, c='green', linewidth=1, label='AC Top [50-200 keV]')
            if FLAG == 'D': ax_AC0.step(AC0[:,0]-TTIME, AC0[:,2], markersize=5, c='green', linewidth=1, label='AC Top [50-200 keV]')
            ax_AC0.set_ylabel('AC TOP\n[counts / s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_AC0.get_xticklabels(), fontsize=18)
            plt.setp(ax_AC0.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_AC0.set_xlim(SX,DX)
            if FLAG == 'ND': ax_AC0.set_ylim(np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1])-np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_AC0.set_ylim(np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2])-np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_MCAL = fig.add_subplot(313)
            if FLAG == 'ND': ax_MCAL.step(MCAL[:,0]-TTIME, MCAL[:,1], markersize=5, c='red', linewidth=1, label='MCAL [0.4-100 MeV]')
            if FLAG == 'D': ax_MCAL.step(MCAL[:,0]-TTIME, MCAL[:,2], markersize=5, c='red', linewidth=1, label='MCAL [0.4-100 MeV]')
            ax_MCAL.set_ylabel('MCAL\n[counts / s]', fontsize=20)
            plt.axvline(x=0, linewidth=2, color = 'black', linestyle = 'dashed', alpha = 0.3)
            plt.setp(ax_MCAL.get_xticklabels(), fontsize=18)
            plt.setp(ax_MCAL.get_yticklabels(), fontsize=18)
            plt.legend(loc='upper right', fontsize=18)
            ax_MCAL.set_xlim(SX,DX)
            if FLAG == 'ND': ax_MCAL.set_ylim(np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]), np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1])-np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]))/3          )
            if FLAG == 'D': ax_MCAL.set_ylim(np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]), np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2])-np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2]))/3          )

            ax_MCAL.set_xlabel('\nt - T0 [s]', fontsize=25)
            if FLAG == 'ND': plt.savefig("%s_RM/%s_AGILE_RM_ND.png" % (NAME, NAME))
            if FLAG == 'D': plt.savefig("%s_RM/%s_AGILE_RM_D.png" % (NAME, NAME))
            plt.close(fig)




        ########################
        # ESTIMATE OF DURATION #
        ########################

        ####################
        # Mini-Calorimeter #
        ####################

        SABKG = np.mean(BKG_SA)

        SAINTEGRALCURVE = []
        SAG = 0
        for g in range(0,len(SA)):
            if (SX <= SA[g][0]-TTIME <= DX):
                if SA[g][1] != 0 :
                    SAG += SA[g][1]-SABKG
                    SAINTEGRALCURVE.append([SA[g][0], SAG])
                elif SA[g][1] == 0 :
                    SAG += SA[g][1]
                    SAINTEGRALCURVE.append([SA[g][0], SAG])
        SAINTEGRALCURVE = np.array(SAINTEGRALCURVE)

        SADUR = []
        SARISE = []
        for o in range(len(SAINTEGRALCURVE)):
            if (GRB_SX <= SAINTEGRALCURVE[o][0]-TTIME <= GRB_DX):
                if (SAINTEGRALCURVE[o][1]-SAINTEGRALCURVE[o-1][1] > 0):
                    SADUR.append(1.024)
                    SARISE.append(SAINTEGRALCURVE[o][0])
        SADUR = np.array(SADUR)
        SARISE = np.array(SARISE)
        SADURATION = np.sum(SADUR)

        ########################
        # Anti-Coincidence Top #
        ########################

        ACBKG = np.mean(BKG_AC0)

        ACINTEGRALCURVE = []
        ACG = 0
        for g in range(0,len(AC0)):
            if (SX <= AC0[g][0]-TTIME <= DX):
                if AC0[g][1] != 0 :
                    ACG += AC0[g][1]-ACBKG
                    ACINTEGRALCURVE.append([AC0[g][0], ACG])
                elif AC0[g][1] == 0 :
                    ACG += AC0[g][1]
                    ACINTEGRALCURVE.append([AC0[g][0], ACG])
        ACINTEGRALCURVE = np.array(ACINTEGRALCURVE)

        ACDUR = []
        ACRISE = []
        for o in range(len(ACINTEGRALCURVE)):
            if (GRB_SX <= ACINTEGRALCURVE[o][0]-TTIME <= GRB_DX):
                if (ACINTEGRALCURVE[o][1]-ACINTEGRALCURVE[o-1][1] > 0):
                    ACDUR.append(1.024)
                    ACRISE.append(ACINTEGRALCURVE[o][0])
        ACDUR = np.array(ACDUR)
        ACRISE = np.array(ACRISE)
        ACDURATION = np.sum(ACDUR)

        ####################
        # Mini-Calorimeter #
        ####################

        MCALBKG = np.mean(BKG_MCAL)

        MCALINTEGRALCURVE = []
        MCALG = 0
        for g in range(0,len(MCAL)):
            if (SX <= MCAL[g][0]-TTIME <= DX):
                if MCAL[g][1] != 0 :
                    MCALG += MCAL[g][1]-MCALBKG
                    MCALINTEGRALCURVE.append([MCAL[g][0], MCALG])
                elif MCAL[g][1] == 0 :
                    MCALG += MCAL[g][1]
                    MCALINTEGRALCURVE.append([MCAL[g][0], MCALG])
        MCALINTEGRALCURVE = np.array(MCALINTEGRALCURVE)

        MCALDUR = []
        MCALRISE = []
        for o in range(len(MCALINTEGRALCURVE)):
            if (GRB_SX <= MCALINTEGRALCURVE[o][0]-TTIME <= GRB_DX):
                if (MCALINTEGRALCURVE[o][1]-MCALINTEGRALCURVE[o-1][1] > 0):
                    MCALDUR.append(1.024)
                    MCALRISE.append(MCALINTEGRALCURVE[o][0])
        MCALDUR = np.array(MCALDUR)
        MCALRISE = np.array(MCALRISE)
        MCALDURATION = np.sum(MCALDUR)

        print("DURATION in SuperAGILE: %3.2f s" % SADURATION)
        print("DURATION in MCAL: %3.2f s" % MCALDURATION)
        print("DURATION in AC Top: %3.2f s" % ACDURATION)

        ###############################
        # PLOT DURATION OF RATEMETERS #
        ###############################

        fig = plt.figure(figsize=(40,16))
        ax1 = fig.add_subplot(2,3,1)
        ax1.step(SA[:,0]-TTIME, SA[:,1], markersize=5, c='black', linewidth=1, label='SA RM [0.4-100 MeV]')
        for j in range(len(SARISE)):
            ax1.axvline(x=SARISE[j]-TTIME, linewidth=3, c='green', linestyle = 'dashed', alpha=0.5)
        ax1.axvspan(SX, DX, alpha=0.03, color='black')
        ax1.axvspan(GRB_SX, GRB_DX, alpha=0.15, color='blue')
        ax1.axvspan(BKG_SX, BKG_DX, alpha=0.15, color='red')
        ax1.axhline(y=SABKG, linewidth=1, c='red', alpha=0.5)
        plt.axhline(y=0, linewidth=1, color = 'red', linestyle = 'dashed', alpha = 1)
        plt.setp(ax1.get_xticklabels(), fontsize=18)
        plt.setp(ax1.get_yticklabels(), fontsize=18)
        plt.legend(loc='upper right', fontsize=20)
        ax1.set_ylabel('SA\n[counts / 0.512 s]', fontsize=20)
        ax1.set_xlim(SX,DX)
        if FLAG == 'ND': ax1.set_ylim(np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]), np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1])-np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]))/3          )
        if FLAG == 'D': ax1.set_ylim(np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 1]), np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2])-np.min(SA[np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][0] : np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0][len(np.where((SA[:,0]>TTIME+SX)&(SA[:,0]<TTIME+DX))[0])-1], 2]))/3          )

        ax2 = fig.add_subplot(2,3,4)
        ax2.step(SAINTEGRALCURVE[:,0]-TTIME, SAINTEGRALCURVE[:,1], markersize=5, c='black', linewidth=1)
        for j in range(len(SARISE)):
            ax2.axvline(x=SARISE[j]-TTIME, linewidth=3, c='green', linestyle = 'dashed', alpha=0.5)
        ax2.axvspan(SX, DX, alpha=0.03, color='black')
        ax2.axvspan(GRB_SX, GRB_DX, alpha=0.15, color='blue')
        ax2.axvspan(BKG_SX, BKG_DX, alpha=0.15, color='red')
        plt.setp(ax2.get_xticklabels(), fontsize=18)
        plt.setp(ax2.get_yticklabels(), fontsize=18)
        ax2.set_xlim(SX,DX)
        plt.legend(loc='lower right', fontsize=20)
        ax2.set_ylabel('integral of SA\n[integr. counts / 0.512 s]', fontsize=20)
        ax2.set_xlabel('t - $\mathregular{T_0}$ [s]', fontsize=20)

        ax3 = fig.add_subplot(2,3,2)
        ax3.step(MCAL[:,0]-TTIME, MCAL[:,1], markersize=5, c='black', linewidth=1, label='MCAL RM [0.4-100 MeV]')
        for j in range(len(MCALRISE)):
            ax3.axvline(x=MCALRISE[j]-TTIME, linewidth=3, c='green', linestyle = 'dashed', alpha=0.5)
        ax3.axvspan(SX, DX, alpha=0.03, color='black')
        ax3.axvspan(GRB_SX, GRB_DX, alpha=0.15, color='blue')
        ax3.axvspan(BKG_SX, BKG_DX, alpha=0.15, color='red')
        plt.setp(ax3.get_xticklabels(), fontsize=18)
        plt.setp(ax3.get_yticklabels(), fontsize=18)
        plt.legend(loc='upper right', fontsize=20)
        ax3.set_ylabel('MCAL\n[counts / 1.024 s]', fontsize=20)
        ax3.set_xlim(SX,DX)
        if FLAG == 'ND': ax3.set_ylim(np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]), np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1])-np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]))/3          )
        if FLAG == 'D': ax3.set_ylim(np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 1]), np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2])-np.min(MCAL[np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][0] : np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0][len(np.where((MCAL[:,0]>TTIME+SX)&(MCAL[:,0]<TTIME+DX))[0])-1], 2]))/3          )

        ax4 = fig.add_subplot(2,3,5)
        ax4.step(MCALINTEGRALCURVE[:,0]-TTIME, MCALINTEGRALCURVE[:,1], markersize=5, c='black', linewidth=1)
        for j in range(len(MCALRISE)):
            ax4.axvline(x=MCALRISE[j]-TTIME, linewidth=3, c='green', linestyle = 'dashed', alpha=0.5)
        ax4.axvspan(SX, DX, alpha=0.03, color='black')
        ax4.axvspan(GRB_SX, GRB_DX, alpha=0.15, color='blue')
        ax4.axvspan(BKG_SX, BKG_DX, alpha=0.15, color='red')
        plt.setp(ax4.get_xticklabels(), fontsize=18)
        plt.setp(ax4.get_yticklabels(), fontsize=18)
        ax4.set_xlim(SX,DX)
        plt.legend(loc='lower right', fontsize=20)
        ax4.set_ylabel('integral of MCAL\n[integr. counts / 1.024 s]', fontsize=20)
        ax4.set_xlabel('t - $\mathregular{T_0}$ [s]', fontsize=20)

        ax5 = fig.add_subplot(2,3,3)
        ax5.step(AC0[:,0]-TTIME, AC0[:,1], markersize=5, c='black', linewidth=1, label='AC Top RM [0.4-100 MeV]')
        for j in range(len(ACRISE)):
            ax5.axvline(x=ACRISE[j]-TTIME, linewidth=3, c='green', linestyle = 'dashed', alpha=0.5)
        ax5.axvspan(SX, DX, alpha=0.03, color='black')
        ax5.axvspan(GRB_SX, GRB_DX, alpha=0.15, color='blue')
        ax5.axvspan(BKG_SX, BKG_DX, alpha=0.15, color='red')
        plt.setp(ax5.get_xticklabels(), fontsize=18)
        plt.setp(ax5.get_yticklabels(), fontsize=18)
        plt.legend(loc='upper right', fontsize=20)
        ax5.set_ylabel('AC Top\n[counts / 1.024 s]', fontsize=20)
        ax5.set_xlim(SX,DX)
        if FLAG == 'ND': ax5.set_ylim(np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]) + (np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1])-np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]))/3          )
        if FLAG == 'D': ax5.set_ylim(np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 1]), np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2]) + (np.max(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2])-np.min(AC0[np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][0] : np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0][len(np.where((AC0[:,0]>TTIME+SX)&(AC0[:,0]<TTIME+DX))[0])-1], 2]))/3          )

        ax6 = fig.add_subplot(2,3,6)
        ax6.step(ACINTEGRALCURVE[:,0]-TTIME, ACINTEGRALCURVE[:,1], markersize=5, c='black', linewidth=1)
        for j in range(len(ACRISE)):
            ax6.axvline(x=ACRISE[j]-TTIME, linewidth=3, c='green', linestyle = 'dashed', alpha=0.5)
        ax6.axvspan(SX, DX, alpha=0.03, color='black')
        ax6.axvspan(GRB_SX, GRB_DX, alpha=0.15, color='blue')
        ax6.axvspan(BKG_SX, BKG_DX, alpha=0.15, color='red')
        plt.setp(ax6.get_xticklabels(), fontsize=18)
        plt.setp(ax6.get_yticklabels(), fontsize=18)
        ax6.set_xlim(SX,DX)
        plt.legend(loc='lower right', fontsize=20)
        ax6.set_ylabel('integral of AC Top\n[integr. counts / 1.024 s]', fontsize=20)
        ax2.set_xlabel('t - $\mathregular{T_0}$ [s]', fontsize=20)

        plt.savefig("%s_RM/%s_DURATION.png" % (NAME, NAME))
        plt.close(fig)
