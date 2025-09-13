# DESCRIPTION
# A. Ursi 2022 #

import numpy as np
import os
import scipy.fftpack

from astropy.io import fits
from astropy.table import Table
from pathlib import Path

from agilepy.core.AGBaseAnalysis import AGBaseAnalysis
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.utils.Utils import Utils


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
        # Load the AGBaseAnalysis object and attributes
        super().__init__(configurationFilePath)
        self.config.loadConfigurationsForClass("AGRatemeters")
        self.logger = self.agilepyLogger.getLogger(__name__, "AGRatemeters")
        
        # Set attributes
        self._ratemetersTables = None
        
        # End initialization
        self.logger.info("AGRatemeters initialized")
    

    @staticmethod
    def getConfiguration(confFilePath, outputDir, filePath, timetype, T0,
                         background_tmin="null", background_tmax="null", signal_tmin="null", signal_tmax="null",
                         userName="my_name", sourceName="rm-source", verboselvl=0,
        ):
        """Utility method to create a configuration file.

        Args:
            confFilePath (str): the path and filename of the configuration file that is going to be created.
            outputDir (str): the path to the output directory. The output directory will be created using the following format: 'userName_sourceName_todaydate'
            filePath (str): The path to the data file. 
            
            timetype (str): Format of the Burst Reference Time T0.
            T0 (float or str): Value of the Burst Reference Time T0.
            background_tmin (float): Min Time for Background computation.
            background_tmax (float): Max Time for Background computation.
            signal_tmin (float): Min Time for Signal computation.
            signal_tmax (float): Max Time for Signal computation.
            
            userName (str): the username of who is running the software.
            sourceName (str): the name of the source.
            verboselvl (int): the verbosity level of the console output. Message types: level 0 => critical, warning, level 1 => critical, warning, info, level 2 => critical, warning, info, debug            

        Returns:
            None
        """

        configuration = f"""

output:
  outdir: {outputDir}
  filenameprefix: ratemeters_product
  sourcename: {sourceName}
  username: {userName}
  verboselvl: {verboselvl}

selection:
  file_path: {filePath}

analysis:
  timetype: \"{timetype}\"
  T0: \"{T0}\"
  background_tmin: {background_tmin}
  background_tmax: {background_tmax}
  signal_tmin: {signal_tmin}
  signal_tmax: {signal_tmax}

        """
        full_file_path = Utils._expandEnvVar(confFilePath)
        parent_directory = Path(full_file_path).absolute().parent
        parent_directory.mkdir(exist_ok=True, parents=True)

        with open(full_file_path,"w") as cf:

            cf.write(configuration)

        return None
    
    def _detrendData(self, data, sampling=0.512, frequency_cut_range=(1.0E-4,1.0E-2)):
        """Apply Detrending algorithm of Background Modulation using Fast Fourier Transform.

        Arguments:
            data (np.array): Array of (Time, Value) data.
            sampling (float): Sampling in seconds to compute the frequencies.
            frequency_cut_range ( (float, float) ): Range of frequencies to cut.
                    
        Return:
        -------
        data_cut_signal (np.array): Detrended values.
        """
        times = data['OBT'].data
        values= data['COUNTS'].data
        
        # Create array of indices, one per time row, then normalize it.
        data_xf = np.arange(len(data))
        data_xf = data_xf/float(times[-1]-times[0])
        
        # Computes the power spectrum (squared magnitude of FFT), normalized by total signal power.
        data_yf = (2 / np.sum(values)) * abs(scipy.fftpack.fft(values))**2 #* scipy.fftpack.rfft(y)
                
        # Truncate to positive frequencies
        half = len(data_xf) // 2
        data_xf = data_xf[:half]
        data_yf = data_yf[:half]
                
        # Computes the real FFT of the signal, and the frequency bins according to the given sampling.
        data_f_signal = scipy.fftpack.rfft(values)
        data_W = scipy.fftpack.fftfreq(len(values), d=sampling)
                
        # Frequency Filtering: keep only low and high frequrencies, then merge
        data_cut_f_signalsx = data_f_signal.copy()
        data_cut_f_signaldx = data_f_signal.copy()
        data_cut_f_signalsx[(data_W>frequency_cut_range[0])] = 0
        data_cut_f_signaldx[(data_W<frequency_cut_range[1])] = 0
        data_cut_f_signal = data_cut_f_signalsx + data_cut_f_signaldx
                
        # Obtain the time-domain signal with Inverse FFT
        data_cut_signal = scipy.fftpack.irfft(data_cut_f_signal)
        
        return data_cut_signal
            
            
    def readRatemeters(self, filePath=None, writeFiles=True):
        """Read a file with ratemeters data and store it in a table.
        The table contains three columns: OBT Time (AGILE TT), Measured Counts, Detrended Counts.
        The detrending algorithm uses Fast Fourier Transforms.
        
        Parameters
        ----------
        filePath (str) : Input file. If None, read from the configuration.
        writeFiles (bool) : Boolean flag to write the ratemeters light curves.
        
        Return
        ------
        ratemeters_table (dict of astropy.Table.table) : each Table contains OBT time (AGILE TT), Counts, Detrended Counts.
        """
        # If arguments are not provided explicitly, set them from the configuration
        filePath = filePath if filePath is not None else self.config.getOptionValue("file_path")
        
        if not os.path.isfile(filePath):
            raise FileNotFoundError
        
        self.logger.info(f"Converting 3913 file: {filePath}")
        
        # From every row of the 1913 file, read appropriate (time, value) and append them to each array.
        # For each row of the 3913 file, append 8 values to each array from different columns,
        # corresponding to 8 acquisition times shifted by (-8.196 + N*1.024), with N ranging from 0 to 7.
        # For SA data, there are 16 columns as the time shift unit is 0.512 second.
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
        

        # Read the input file
        # f"/ASDC_PROC2/DATA_2/COR/PKP{CONT}_1_3913_000.lv1.cor.gz"
        with fits.open(filePath) as hdulist:
            tbdata = hdulist[1].data

            for i in range(0,int(tbdata.shape[0])):
                
                base_time = float(tbdata[i][19])

                ###################
                # SILICON TRACKER #
                ###################

                GRID_1X.append([base_time+0.000-8.196, int(tbdata[i][25])])
                GRID_1X.append([base_time+1.024-8.196, int(tbdata[i][37])])
                GRID_1X.append([base_time+2.048-8.196, int(tbdata[i][49])])
                GRID_1X.append([base_time+3.072-8.196, int(tbdata[i][61])])
                GRID_1X.append([base_time+4.096-8.196, int(tbdata[i][73])])
                GRID_1X.append([base_time+5.120-8.196, int(tbdata[i][85])])
                GRID_1X.append([base_time+6.144-8.196, int(tbdata[i][97])])
                GRID_1X.append([base_time+7.168-8.196, int(tbdata[i][109])])

                GRID_2X.append([base_time+0.000-8.196, int(tbdata[i][26])])
                GRID_2X.append([base_time+1.024-8.196, int(tbdata[i][38])])
                GRID_2X.append([base_time+2.048-8.196, int(tbdata[i][50])])
                GRID_2X.append([base_time+3.072-8.196, int(tbdata[i][62])])
                GRID_2X.append([base_time+4.096-8.196, int(tbdata[i][74])])
                GRID_2X.append([base_time+5.120-8.196, int(tbdata[i][86])])
                GRID_2X.append([base_time+6.144-8.196, int(tbdata[i][98])])
                GRID_2X.append([base_time+7.168-8.196, int(tbdata[i][110])])

                GRID_3X.append([base_time+0.000-8.196, int(tbdata[i][27])])
                GRID_3X.append([base_time+1.024-8.196, int(tbdata[i][39])])
                GRID_3X.append([base_time+2.048-8.196, int(tbdata[i][51])])
                GRID_3X.append([base_time+3.072-8.196, int(tbdata[i][63])])
                GRID_3X.append([base_time+4.096-8.196, int(tbdata[i][75])])
                GRID_3X.append([base_time+5.120-8.196, int(tbdata[i][87])])
                GRID_3X.append([base_time+6.144-8.196, int(tbdata[i][99])])
                GRID_3X.append([base_time+7.168-8.196, int(tbdata[i][111])])

                GRID_4X.append([base_time+0.000-8.196, int(tbdata[i][28])])
                GRID_4X.append([base_time+1.024-8.196, int(tbdata[i][40])])
                GRID_4X.append([base_time+2.048-8.196, int(tbdata[i][52])])
                GRID_4X.append([base_time+3.072-8.196, int(tbdata[i][64])])
                GRID_4X.append([base_time+4.096-8.196, int(tbdata[i][76])])
                GRID_4X.append([base_time+5.120-8.196, int(tbdata[i][88])])
                GRID_4X.append([base_time+6.144-8.196, int(tbdata[i][100])])
                GRID_4X.append([base_time+7.168-8.196, int(tbdata[i][112])])

                GRID_5X.append([base_time+0.000-8.196, int(tbdata[i][29])])
                GRID_5X.append([base_time+1.024-8.196, int(tbdata[i][41])])
                GRID_5X.append([base_time+2.048-8.196, int(tbdata[i][53])])
                GRID_5X.append([base_time+3.072-8.196, int(tbdata[i][65])])
                GRID_5X.append([base_time+4.096-8.196, int(tbdata[i][77])])
                GRID_5X.append([base_time+5.120-8.196, int(tbdata[i][89])])
                GRID_5X.append([base_time+6.144-8.196, int(tbdata[i][101])])
                GRID_5X.append([base_time+7.168-8.196, int(tbdata[i][113])])

                GRID_6X.append([base_time+0.000-8.196, int(tbdata[i][30])])
                GRID_6X.append([base_time+1.024-8.196, int(tbdata[i][42])])
                GRID_6X.append([base_time+2.048-8.196, int(tbdata[i][54])])
                GRID_6X.append([base_time+3.072-8.196, int(tbdata[i][66])])
                GRID_6X.append([base_time+4.096-8.196, int(tbdata[i][78])])
                GRID_6X.append([base_time+5.120-8.196, int(tbdata[i][90])])
                GRID_6X.append([base_time+6.144-8.196, int(tbdata[i][102])])
                GRID_6X.append([base_time+7.168-8.196, int(tbdata[i][114])])

                GRID_1Z.append([base_time+0.000-8.196, int(tbdata[i][31])])
                GRID_1Z.append([base_time+1.024-8.196, int(tbdata[i][43])])
                GRID_1Z.append([base_time+2.048-8.196, int(tbdata[i][55])])
                GRID_1Z.append([base_time+3.072-8.196, int(tbdata[i][67])])
                GRID_1Z.append([base_time+4.096-8.196, int(tbdata[i][79])])
                GRID_1Z.append([base_time+5.120-8.196, int(tbdata[i][91])])
                GRID_1Z.append([base_time+6.144-8.196, int(tbdata[i][103])])
                GRID_1Z.append([base_time+7.168-8.196, int(tbdata[i][115])])

                GRID_2Z.append([base_time+0.000-8.196, int(tbdata[i][32])])
                GRID_2Z.append([base_time+1.024-8.196, int(tbdata[i][44])])
                GRID_2Z.append([base_time+2.048-8.196, int(tbdata[i][56])])
                GRID_2Z.append([base_time+3.072-8.196, int(tbdata[i][68])])
                GRID_2Z.append([base_time+4.096-8.196, int(tbdata[i][80])])
                GRID_2Z.append([base_time+5.120-8.196, int(tbdata[i][92])])
                GRID_2Z.append([base_time+6.144-8.196, int(tbdata[i][104])])
                GRID_2Z.append([base_time+7.168-8.196, int(tbdata[i][116])])

                GRID_3Z.append([base_time+0.000-8.196, int(tbdata[i][33])])
                GRID_3Z.append([base_time+1.024-8.196, int(tbdata[i][45])])
                GRID_3Z.append([base_time+2.048-8.196, int(tbdata[i][57])])
                GRID_3Z.append([base_time+3.072-8.196, int(tbdata[i][69])])
                GRID_3Z.append([base_time+4.096-8.196, int(tbdata[i][81])])
                GRID_3Z.append([base_time+5.120-8.196, int(tbdata[i][93])])
                GRID_3Z.append([base_time+6.144-8.196, int(tbdata[i][105])])
                GRID_3Z.append([base_time+7.168-8.196, int(tbdata[i][117])])

                GRID_4Z.append([base_time+0.000-8.196, int(tbdata[i][34])])
                GRID_4Z.append([base_time+1.024-8.196, int(tbdata[i][46])])
                GRID_4Z.append([base_time+2.048-8.196, int(tbdata[i][58])])
                GRID_4Z.append([base_time+3.072-8.196, int(tbdata[i][70])])
                GRID_4Z.append([base_time+4.096-8.196, int(tbdata[i][82])])
                GRID_4Z.append([base_time+5.120-8.196, int(tbdata[i][94])])
                GRID_4Z.append([base_time+6.144-8.196, int(tbdata[i][106])])
                GRID_4Z.append([base_time+7.168-8.196, int(tbdata[i][118])])

                GRID_5Z.append([base_time+0.000-8.196, int(tbdata[i][35])])
                GRID_5Z.append([base_time+1.024-8.196, int(tbdata[i][47])])
                GRID_5Z.append([base_time+2.048-8.196, int(tbdata[i][59])])
                GRID_5Z.append([base_time+3.072-8.196, int(tbdata[i][71])])
                GRID_5Z.append([base_time+4.096-8.196, int(tbdata[i][83])])
                GRID_5Z.append([base_time+5.120-8.196, int(tbdata[i][95])])
                GRID_5Z.append([base_time+6.144-8.196, int(tbdata[i][107])])
                GRID_5Z.append([base_time+7.168-8.196, int(tbdata[i][119])])

                GRID_6Z.append([base_time+0.000-8.196, int(tbdata[i][36])])
                GRID_6Z.append([base_time+1.024-8.196, int(tbdata[i][48])])
                GRID_6Z.append([base_time+2.048-8.196, int(tbdata[i][60])])
                GRID_6Z.append([base_time+3.072-8.196, int(tbdata[i][72])])
                GRID_6Z.append([base_time+4.096-8.196, int(tbdata[i][84])])
                GRID_6Z.append([base_time+5.120-8.196, int(tbdata[i][96])])
                GRID_6Z.append([base_time+6.144-8.196, int(tbdata[i][108])])
                GRID_6Z.append([base_time+7.168-8.196, int(tbdata[i][120])])

                ####################
                # ANTI-COINCIDENCE #
                ####################

                AC_SIDE0.append([base_time+0.000-8.196, int(tbdata[i][121])])
                AC_SIDE0.append([base_time+1.024-8.196, int(tbdata[i][126])])
                AC_SIDE0.append([base_time+2.048-8.196, int(tbdata[i][131])])
                AC_SIDE0.append([base_time+3.072-8.196, int(tbdata[i][136])])
                AC_SIDE0.append([base_time+4.096-8.196, int(tbdata[i][141])])
                AC_SIDE0.append([base_time+5.120-8.196, int(tbdata[i][146])])
                AC_SIDE0.append([base_time+6.144-8.196, int(tbdata[i][151])])
                AC_SIDE0.append([base_time+7.168-8.196, int(tbdata[i][156])])

                AC_SIDE1.append([base_time+0.000-8.196, int(tbdata[i][122])])
                AC_SIDE1.append([base_time+1.024-8.196, int(tbdata[i][127])])
                AC_SIDE1.append([base_time+2.048-8.196, int(tbdata[i][132])])
                AC_SIDE1.append([base_time+3.072-8.196, int(tbdata[i][137])])
                AC_SIDE1.append([base_time+4.096-8.196, int(tbdata[i][142])])
                AC_SIDE1.append([base_time+5.120-8.196, int(tbdata[i][147])])
                AC_SIDE1.append([base_time+6.144-8.196, int(tbdata[i][152])])
                AC_SIDE1.append([base_time+7.168-8.196, int(tbdata[i][157])])

                AC_SIDE2.append([base_time+0.000-8.196, int(tbdata[i][123])])
                AC_SIDE2.append([base_time+1.024-8.196, int(tbdata[i][128])])
                AC_SIDE2.append([base_time+2.048-8.196, int(tbdata[i][133])])
                AC_SIDE2.append([base_time+3.072-8.196, int(tbdata[i][138])])
                AC_SIDE2.append([base_time+4.096-8.196, int(tbdata[i][143])])
                AC_SIDE2.append([base_time+5.120-8.196, int(tbdata[i][148])])
                AC_SIDE2.append([base_time+6.144-8.196, int(tbdata[i][153])])
                AC_SIDE2.append([base_time+7.168-8.196, int(tbdata[i][158])])

                AC_SIDE3.append([base_time+0.000-8.196, int(tbdata[i][124])])
                AC_SIDE3.append([base_time+1.024-8.196, int(tbdata[i][129])])
                AC_SIDE3.append([base_time+2.048-8.196, int(tbdata[i][134])])
                AC_SIDE3.append([base_time+3.072-8.196, int(tbdata[i][139])])
                AC_SIDE3.append([base_time+4.096-8.196, int(tbdata[i][144])])
                AC_SIDE3.append([base_time+5.120-8.196, int(tbdata[i][149])])
                AC_SIDE3.append([base_time+6.144-8.196, int(tbdata[i][154])])
                AC_SIDE3.append([base_time+7.168-8.196, int(tbdata[i][159])])

                AC_SIDE4.append([base_time+0.000-8.196, int(tbdata[i][125])])
                AC_SIDE4.append([base_time+1.024-8.196, int(tbdata[i][130])])
                AC_SIDE4.append([base_time+2.048-8.196, int(tbdata[i][135])])
                AC_SIDE4.append([base_time+3.072-8.196, int(tbdata[i][140])])
                AC_SIDE4.append([base_time+4.096-8.196, int(tbdata[i][145])])
                AC_SIDE4.append([base_time+5.120-8.196, int(tbdata[i][150])])
                AC_SIDE4.append([base_time+6.144-8.196, int(tbdata[i][155])])
                AC_SIDE4.append([base_time+7.168-8.196, int(tbdata[i][160])])

                ####################
                # MINI-CALORIMETER #
                ####################

                MCAL_X_CH01.append([base_time+0.000-8.196, int(tbdata[i][161])])
                MCAL_X_CH01.append([base_time+1.024-8.196, int(tbdata[i][183])])
                MCAL_X_CH01.append([base_time+2.048-8.196, int(tbdata[i][205])])
                MCAL_X_CH01.append([base_time+3.072-8.196, int(tbdata[i][227])])
                MCAL_X_CH01.append([base_time+4.096-8.196, int(tbdata[i][249])])
                MCAL_X_CH01.append([base_time+5.120-8.196, int(tbdata[i][271])])
                MCAL_X_CH01.append([base_time+6.144-8.196, int(tbdata[i][293])])
                MCAL_X_CH01.append([base_time+7.168-8.196, int(tbdata[i][315])])

                MCAL_X_CH02.append([base_time+0.000-8.196, int(tbdata[i][162])])
                MCAL_X_CH02.append([base_time+1.024-8.196, int(tbdata[i][184])])
                MCAL_X_CH02.append([base_time+2.048-8.196, int(tbdata[i][206])])
                MCAL_X_CH02.append([base_time+3.072-8.196, int(tbdata[i][228])])
                MCAL_X_CH02.append([base_time+4.096-8.196, int(tbdata[i][250])])
                MCAL_X_CH02.append([base_time+5.120-8.196, int(tbdata[i][272])])
                MCAL_X_CH02.append([base_time+6.144-8.196, int(tbdata[i][294])])
                MCAL_X_CH02.append([base_time+7.168-8.196, int(tbdata[i][316])])

                MCAL_X_CH03.append([base_time+0.000-8.196, int(tbdata[i][163])])
                MCAL_X_CH03.append([base_time+1.024-8.196, int(tbdata[i][185])])
                MCAL_X_CH03.append([base_time+2.048-8.196, int(tbdata[i][207])])
                MCAL_X_CH03.append([base_time+3.072-8.196, int(tbdata[i][229])])
                MCAL_X_CH03.append([base_time+4.096-8.196, int(tbdata[i][251])])
                MCAL_X_CH03.append([base_time+5.120-8.196, int(tbdata[i][273])])
                MCAL_X_CH03.append([base_time+6.144-8.196, int(tbdata[i][295])])
                MCAL_X_CH03.append([base_time+7.168-8.196, int(tbdata[i][317])])

                MCAL_X_CH04.append([base_time+0.000-8.196, int(tbdata[i][164])])
                MCAL_X_CH04.append([base_time+1.024-8.196, int(tbdata[i][186])])
                MCAL_X_CH04.append([base_time+2.048-8.196, int(tbdata[i][208])])
                MCAL_X_CH04.append([base_time+3.072-8.196, int(tbdata[i][230])])
                MCAL_X_CH04.append([base_time+4.096-8.196, int(tbdata[i][252])])
                MCAL_X_CH04.append([base_time+5.120-8.196, int(tbdata[i][274])])
                MCAL_X_CH04.append([base_time+6.144-8.196, int(tbdata[i][296])])
                MCAL_X_CH04.append([base_time+7.168-8.196, int(tbdata[i][318])])

                MCAL_X_CH05.append([base_time+0.000-8.196, int(tbdata[i][165])])
                MCAL_X_CH05.append([base_time+1.024-8.196, int(tbdata[i][187])])
                MCAL_X_CH05.append([base_time+2.048-8.196, int(tbdata[i][209])])
                MCAL_X_CH05.append([base_time+3.072-8.196, int(tbdata[i][231])])
                MCAL_X_CH05.append([base_time+4.096-8.196, int(tbdata[i][253])])
                MCAL_X_CH05.append([base_time+5.120-8.196, int(tbdata[i][275])])
                MCAL_X_CH05.append([base_time+6.144-8.196, int(tbdata[i][297])])
                MCAL_X_CH05.append([base_time+7.168-8.196, int(tbdata[i][319])])

                MCAL_X_CH06.append([base_time+0.000-8.196, int(tbdata[i][166])])
                MCAL_X_CH06.append([base_time+1.024-8.196, int(tbdata[i][188])])
                MCAL_X_CH06.append([base_time+2.048-8.196, int(tbdata[i][210])])
                MCAL_X_CH06.append([base_time+3.072-8.196, int(tbdata[i][232])])
                MCAL_X_CH06.append([base_time+4.096-8.196, int(tbdata[i][254])])
                MCAL_X_CH06.append([base_time+5.120-8.196, int(tbdata[i][276])])
                MCAL_X_CH06.append([base_time+6.144-8.196, int(tbdata[i][298])])
                MCAL_X_CH06.append([base_time+7.168-8.196, int(tbdata[i][320])])

                MCAL_X_CH07.append([base_time+0.000-8.196, int(tbdata[i][167])])
                MCAL_X_CH07.append([base_time+1.024-8.196, int(tbdata[i][189])])
                MCAL_X_CH07.append([base_time+2.048-8.196, int(tbdata[i][211])])
                MCAL_X_CH07.append([base_time+3.072-8.196, int(tbdata[i][233])])
                MCAL_X_CH07.append([base_time+4.096-8.196, int(tbdata[i][255])])
                MCAL_X_CH07.append([base_time+5.120-8.196, int(tbdata[i][277])])
                MCAL_X_CH07.append([base_time+6.144-8.196, int(tbdata[i][299])])
                MCAL_X_CH07.append([base_time+7.168-8.196, int(tbdata[i][321])])

                MCAL_X_CH08.append([base_time+0.000-8.196, int(tbdata[i][168])])
                MCAL_X_CH08.append([base_time+1.024-8.196, int(tbdata[i][190])])
                MCAL_X_CH08.append([base_time+2.048-8.196, int(tbdata[i][212])])
                MCAL_X_CH08.append([base_time+3.072-8.196, int(tbdata[i][234])])
                MCAL_X_CH08.append([base_time+4.096-8.196, int(tbdata[i][256])])
                MCAL_X_CH08.append([base_time+5.120-8.196, int(tbdata[i][278])])
                MCAL_X_CH08.append([base_time+6.144-8.196, int(tbdata[i][300])])
                MCAL_X_CH08.append([base_time+7.168-8.196, int(tbdata[i][322])])

                MCAL_X_CH09.append([base_time+0.000-8.196, int(tbdata[i][169])])
                MCAL_X_CH09.append([base_time+1.024-8.196, int(tbdata[i][191])])
                MCAL_X_CH09.append([base_time+2.048-8.196, int(tbdata[i][213])])
                MCAL_X_CH09.append([base_time+3.072-8.196, int(tbdata[i][235])])
                MCAL_X_CH09.append([base_time+4.096-8.196, int(tbdata[i][257])])
                MCAL_X_CH09.append([base_time+5.120-8.196, int(tbdata[i][279])])
                MCAL_X_CH09.append([base_time+6.144-8.196, int(tbdata[i][301])])
                MCAL_X_CH09.append([base_time+7.168-8.196, int(tbdata[i][323])])

                MCAL_X_CH10.append([base_time+0.000-8.196, int(tbdata[i][170])])
                MCAL_X_CH10.append([base_time+1.024-8.196, int(tbdata[i][192])])
                MCAL_X_CH10.append([base_time+2.048-8.196, int(tbdata[i][214])])
                MCAL_X_CH10.append([base_time+3.072-8.196, int(tbdata[i][236])])
                MCAL_X_CH10.append([base_time+4.096-8.196, int(tbdata[i][258])])
                MCAL_X_CH10.append([base_time+5.120-8.196, int(tbdata[i][280])])
                MCAL_X_CH10.append([base_time+6.144-8.196, int(tbdata[i][302])])
                MCAL_X_CH10.append([base_time+7.168-8.196, int(tbdata[i][324])])

                MCAL_X_CH11.append([base_time+0.000-8.196, int(tbdata[i][171])])
                MCAL_X_CH11.append([base_time+1.024-8.196, int(tbdata[i][193])])
                MCAL_X_CH11.append([base_time+2.048-8.196, int(tbdata[i][215])])
                MCAL_X_CH11.append([base_time+3.072-8.196, int(tbdata[i][237])])
                MCAL_X_CH11.append([base_time+4.096-8.196, int(tbdata[i][259])])
                MCAL_X_CH11.append([base_time+5.120-8.196, int(tbdata[i][281])])
                MCAL_X_CH11.append([base_time+6.144-8.196, int(tbdata[i][303])])
                MCAL_X_CH11.append([base_time+7.168-8.196, int(tbdata[i][325])])

                MCAL_Z_CH01.append([base_time+0.000-8.196, int(tbdata[i][172])])
                MCAL_Z_CH01.append([base_time+1.024-8.196, int(tbdata[i][194])])
                MCAL_Z_CH01.append([base_time+2.048-8.196, int(tbdata[i][216])])
                MCAL_Z_CH01.append([base_time+3.072-8.196, int(tbdata[i][238])])
                MCAL_Z_CH01.append([base_time+4.096-8.196, int(tbdata[i][260])])
                MCAL_Z_CH01.append([base_time+5.120-8.196, int(tbdata[i][282])])
                MCAL_Z_CH01.append([base_time+6.144-8.196, int(tbdata[i][304])])
                MCAL_Z_CH01.append([base_time+7.168-8.196, int(tbdata[i][326])])

                MCAL_Z_CH02.append([base_time+0.000-8.196, int(tbdata[i][173])])
                MCAL_Z_CH02.append([base_time+1.024-8.196, int(tbdata[i][195])])
                MCAL_Z_CH02.append([base_time+2.048-8.196, int(tbdata[i][217])])
                MCAL_Z_CH02.append([base_time+3.072-8.196, int(tbdata[i][239])])
                MCAL_Z_CH02.append([base_time+4.096-8.196, int(tbdata[i][261])])
                MCAL_Z_CH02.append([base_time+5.120-8.196, int(tbdata[i][283])])
                MCAL_Z_CH02.append([base_time+6.144-8.196, int(tbdata[i][305])])
                MCAL_Z_CH02.append([base_time+7.168-8.196, int(tbdata[i][327])])

                MCAL_Z_CH03.append([base_time+0.000-8.196, int(tbdata[i][174])])
                MCAL_Z_CH03.append([base_time+1.024-8.196, int(tbdata[i][196])])
                MCAL_Z_CH03.append([base_time+2.048-8.196, int(tbdata[i][218])])
                MCAL_Z_CH03.append([base_time+3.072-8.196, int(tbdata[i][240])])
                MCAL_Z_CH03.append([base_time+4.096-8.196, int(tbdata[i][262])])
                MCAL_Z_CH03.append([base_time+5.120-8.196, int(tbdata[i][284])])
                MCAL_Z_CH03.append([base_time+6.144-8.196, int(tbdata[i][306])])
                MCAL_Z_CH03.append([base_time+7.168-8.196, int(tbdata[i][328])])

                MCAL_Z_CH04.append([base_time+0.000-8.196, int(tbdata[i][175])])
                MCAL_Z_CH04.append([base_time+1.024-8.196, int(tbdata[i][197])])
                MCAL_Z_CH04.append([base_time+2.048-8.196, int(tbdata[i][219])])
                MCAL_Z_CH04.append([base_time+3.072-8.196, int(tbdata[i][241])])
                MCAL_Z_CH04.append([base_time+4.096-8.196, int(tbdata[i][262])])
                MCAL_Z_CH04.append([base_time+5.120-8.196, int(tbdata[i][285])])
                MCAL_Z_CH04.append([base_time+6.144-8.196, int(tbdata[i][307])])
                MCAL_Z_CH04.append([base_time+7.168-8.196, int(tbdata[i][329])])

                MCAL_Z_CH05.append([base_time+0.000-8.196, int(tbdata[i][176])])
                MCAL_Z_CH05.append([base_time+1.024-8.196, int(tbdata[i][198])])
                MCAL_Z_CH05.append([base_time+2.048-8.196, int(tbdata[i][220])])
                MCAL_Z_CH05.append([base_time+3.072-8.196, int(tbdata[i][242])])
                MCAL_Z_CH05.append([base_time+4.096-8.196, int(tbdata[i][264])])
                MCAL_Z_CH05.append([base_time+5.120-8.196, int(tbdata[i][286])])
                MCAL_Z_CH05.append([base_time+6.144-8.196, int(tbdata[i][308])])
                MCAL_Z_CH05.append([base_time+7.168-8.196, int(tbdata[i][330])])

                MCAL_Z_CH06.append([base_time+0.000-8.196, int(tbdata[i][177])])
                MCAL_Z_CH06.append([base_time+1.024-8.196, int(tbdata[i][199])])
                MCAL_Z_CH06.append([base_time+2.048-8.196, int(tbdata[i][221])])
                MCAL_Z_CH06.append([base_time+3.072-8.196, int(tbdata[i][243])])
                MCAL_Z_CH06.append([base_time+4.096-8.196, int(tbdata[i][265])])
                MCAL_Z_CH06.append([base_time+5.120-8.196, int(tbdata[i][287])])
                MCAL_Z_CH06.append([base_time+6.144-8.196, int(tbdata[i][309])])
                MCAL_Z_CH06.append([base_time+7.168-8.196, int(tbdata[i][331])])

                MCAL_Z_CH07.append([base_time+0.000-8.196, int(tbdata[i][178])])
                MCAL_Z_CH07.append([base_time+1.024-8.196, int(tbdata[i][200])])
                MCAL_Z_CH07.append([base_time+2.048-8.196, int(tbdata[i][222])])
                MCAL_Z_CH07.append([base_time+3.072-8.196, int(tbdata[i][244])])
                MCAL_Z_CH07.append([base_time+4.096-8.196, int(tbdata[i][266])])
                MCAL_Z_CH07.append([base_time+5.120-8.196, int(tbdata[i][288])])
                MCAL_Z_CH07.append([base_time+6.144-8.196, int(tbdata[i][310])])
                MCAL_Z_CH07.append([base_time+7.168-8.196, int(tbdata[i][332])])

                MCAL_Z_CH08.append([base_time+0.000-8.196, int(tbdata[i][179])])
                MCAL_Z_CH08.append([base_time+1.024-8.196, int(tbdata[i][201])])
                MCAL_Z_CH08.append([base_time+2.048-8.196, int(tbdata[i][223])])
                MCAL_Z_CH08.append([base_time+3.072-8.196, int(tbdata[i][245])])
                MCAL_Z_CH08.append([base_time+4.096-8.196, int(tbdata[i][267])])
                MCAL_Z_CH08.append([base_time+5.120-8.196, int(tbdata[i][289])])
                MCAL_Z_CH08.append([base_time+6.144-8.196, int(tbdata[i][311])])
                MCAL_Z_CH08.append([base_time+7.168-8.196, int(tbdata[i][333])])

                MCAL_Z_CH09.append([base_time+0.000-8.196, int(tbdata[i][180])])
                MCAL_Z_CH09.append([base_time+1.024-8.196, int(tbdata[i][202])])
                MCAL_Z_CH09.append([base_time+2.048-8.196, int(tbdata[i][224])])
                MCAL_Z_CH09.append([base_time+3.072-8.196, int(tbdata[i][246])])
                MCAL_Z_CH09.append([base_time+4.096-8.196, int(tbdata[i][268])])
                MCAL_Z_CH09.append([base_time+5.120-8.196, int(tbdata[i][290])])
                MCAL_Z_CH09.append([base_time+6.144-8.196, int(tbdata[i][312])])
                MCAL_Z_CH09.append([base_time+7.168-8.196, int(tbdata[i][334])])

                MCAL_Z_CH10.append([base_time+0.000-8.196, int(tbdata[i][181])])
                MCAL_Z_CH10.append([base_time+1.024-8.196, int(tbdata[i][203])])
                MCAL_Z_CH10.append([base_time+2.048-8.196, int(tbdata[i][225])])
                MCAL_Z_CH10.append([base_time+3.072-8.196, int(tbdata[i][247])])
                MCAL_Z_CH10.append([base_time+4.096-8.196, int(tbdata[i][269])])
                MCAL_Z_CH10.append([base_time+5.120-8.196, int(tbdata[i][291])])
                MCAL_Z_CH10.append([base_time+6.144-8.196, int(tbdata[i][313])])
                MCAL_Z_CH10.append([base_time+7.168-8.196, int(tbdata[i][335])])

                MCAL_Z_CH11.append([base_time+0.000-8.196, int(tbdata[i][182])])
                MCAL_Z_CH11.append([base_time+1.024-8.196, int(tbdata[i][204])])
                MCAL_Z_CH11.append([base_time+2.048-8.196, int(tbdata[i][226])])
                MCAL_Z_CH11.append([base_time+3.072-8.196, int(tbdata[i][248])])
                MCAL_Z_CH11.append([base_time+4.096-8.196, int(tbdata[i][270])])
                MCAL_Z_CH11.append([base_time+5.120-8.196, int(tbdata[i][292])])
                MCAL_Z_CH11.append([base_time+6.144-8.196, int(tbdata[i][314])])
                MCAL_Z_CH11.append([base_time+7.168-8.196, int(tbdata[i][336])])

                ###############
                # SUPER-AGILE #
                ###############

                SA_DET1_LAD1_CH1.append([base_time+0.000-8.196, int(tbdata[i][337])])
                SA_DET1_LAD1_CH1.append([base_time+0.512-8.196, int(tbdata[i][361])])
                SA_DET1_LAD1_CH1.append([base_time+1.024-8.196, int(tbdata[i][385])])
                SA_DET1_LAD1_CH1.append([base_time+1.536-8.196, int(tbdata[i][409])])
                SA_DET1_LAD1_CH1.append([base_time+2.048-8.196, int(tbdata[i][433])])
                SA_DET1_LAD1_CH1.append([base_time+2.560-8.196, int(tbdata[i][457])])
                SA_DET1_LAD1_CH1.append([base_time+3.072-8.196, int(tbdata[i][481])])
                SA_DET1_LAD1_CH1.append([base_time+3.584-8.196, int(tbdata[i][505])])
                SA_DET1_LAD1_CH1.append([base_time+4.096-8.196, int(tbdata[i][529])])
                SA_DET1_LAD1_CH1.append([base_time+4.608-8.196, int(tbdata[i][553])])
                SA_DET1_LAD1_CH1.append([base_time+5.120-8.196, int(tbdata[i][577])])
                SA_DET1_LAD1_CH1.append([base_time+5.632-8.196, int(tbdata[i][601])])
                SA_DET1_LAD1_CH1.append([base_time+6.144-8.196, int(tbdata[i][625])])
                SA_DET1_LAD1_CH1.append([base_time+6.656-8.196, int(tbdata[i][649])])
                SA_DET1_LAD1_CH1.append([base_time+7.168-8.196, int(tbdata[i][673])])
                SA_DET1_LAD1_CH1.append([base_time+7.680-8.196, int(tbdata[i][697])])

                SA_DET1_LAD1_CH2.append([base_time+0.000-8.196, int(tbdata[i][338])])
                SA_DET1_LAD1_CH2.append([base_time+0.512-8.196, int(tbdata[i][362])])
                SA_DET1_LAD1_CH2.append([base_time+1.024-8.196, int(tbdata[i][386])])
                SA_DET1_LAD1_CH2.append([base_time+1.536-8.196, int(tbdata[i][410])])
                SA_DET1_LAD1_CH2.append([base_time+2.048-8.196, int(tbdata[i][434])])
                SA_DET1_LAD1_CH2.append([base_time+2.560-8.196, int(tbdata[i][458])])
                SA_DET1_LAD1_CH2.append([base_time+3.072-8.196, int(tbdata[i][482])])
                SA_DET1_LAD1_CH2.append([base_time+3.584-8.196, int(tbdata[i][506])])
                SA_DET1_LAD1_CH2.append([base_time+4.096-8.196, int(tbdata[i][530])])
                SA_DET1_LAD1_CH2.append([base_time+4.608-8.196, int(tbdata[i][554])])
                SA_DET1_LAD1_CH2.append([base_time+5.120-8.196, int(tbdata[i][578])])
                SA_DET1_LAD1_CH2.append([base_time+5.632-8.196, int(tbdata[i][602])])
                SA_DET1_LAD1_CH2.append([base_time+6.144-8.196, int(tbdata[i][626])])
                SA_DET1_LAD1_CH2.append([base_time+6.656-8.196, int(tbdata[i][650])])
                SA_DET1_LAD1_CH2.append([base_time+7.168-8.196, int(tbdata[i][674])])
                SA_DET1_LAD1_CH2.append([base_time+7.680-8.196, int(tbdata[i][698])])

                SA_DET1_LAD1_CH3.append([base_time+0.000-8.196, int(tbdata[i][339])])
                SA_DET1_LAD1_CH3.append([base_time+0.512-8.196, int(tbdata[i][363])])
                SA_DET1_LAD1_CH3.append([base_time+1.024-8.196, int(tbdata[i][387])])
                SA_DET1_LAD1_CH3.append([base_time+1.536-8.196, int(tbdata[i][411])])
                SA_DET1_LAD1_CH3.append([base_time+2.048-8.196, int(tbdata[i][435])])
                SA_DET1_LAD1_CH3.append([base_time+2.560-8.196, int(tbdata[i][459])])
                SA_DET1_LAD1_CH3.append([base_time+3.072-8.196, int(tbdata[i][483])])
                SA_DET1_LAD1_CH3.append([base_time+3.584-8.196, int(tbdata[i][507])])
                SA_DET1_LAD1_CH3.append([base_time+4.096-8.196, int(tbdata[i][531])])
                SA_DET1_LAD1_CH3.append([base_time+4.608-8.196, int(tbdata[i][555])])
                SA_DET1_LAD1_CH3.append([base_time+5.120-8.196, int(tbdata[i][579])])
                SA_DET1_LAD1_CH3.append([base_time+5.632-8.196, int(tbdata[i][603])])
                SA_DET1_LAD1_CH3.append([base_time+6.144-8.196, int(tbdata[i][627])])
                SA_DET1_LAD1_CH3.append([base_time+6.656-8.196, int(tbdata[i][651])])
                SA_DET1_LAD1_CH3.append([base_time+7.168-8.196, int(tbdata[i][675])])
                SA_DET1_LAD1_CH3.append([base_time+7.680-8.196, int(tbdata[i][699])])

                SA_DET1_LAD2_CH1.append([base_time+0.000-8.196, int(tbdata[i][340])])
                SA_DET1_LAD2_CH1.append([base_time+0.512-8.196, int(tbdata[i][364])])
                SA_DET1_LAD2_CH1.append([base_time+1.024-8.196, int(tbdata[i][388])])
                SA_DET1_LAD2_CH1.append([base_time+1.536-8.196, int(tbdata[i][412])])
                SA_DET1_LAD2_CH1.append([base_time+2.048-8.196, int(tbdata[i][436])])
                SA_DET1_LAD2_CH1.append([base_time+2.560-8.196, int(tbdata[i][460])])
                SA_DET1_LAD2_CH1.append([base_time+3.072-8.196, int(tbdata[i][484])])
                SA_DET1_LAD2_CH1.append([base_time+3.584-8.196, int(tbdata[i][508])])
                SA_DET1_LAD2_CH1.append([base_time+4.096-8.196, int(tbdata[i][532])])
                SA_DET1_LAD2_CH1.append([base_time+4.608-8.196, int(tbdata[i][556])])
                SA_DET1_LAD2_CH1.append([base_time+5.120-8.196, int(tbdata[i][580])])
                SA_DET1_LAD2_CH1.append([base_time+5.632-8.196, int(tbdata[i][604])])
                SA_DET1_LAD2_CH1.append([base_time+6.144-8.196, int(tbdata[i][628])])
                SA_DET1_LAD2_CH1.append([base_time+6.656-8.196, int(tbdata[i][652])])
                SA_DET1_LAD2_CH1.append([base_time+7.168-8.196, int(tbdata[i][676])])
                SA_DET1_LAD2_CH1.append([base_time+7.680-8.196, int(tbdata[i][700])])

                SA_DET1_LAD2_CH2.append([base_time+0.000-8.196, int(tbdata[i][341])])
                SA_DET1_LAD2_CH2.append([base_time+0.512-8.196, int(tbdata[i][365])])
                SA_DET1_LAD2_CH2.append([base_time+1.024-8.196, int(tbdata[i][389])])
                SA_DET1_LAD2_CH2.append([base_time+1.536-8.196, int(tbdata[i][413])])
                SA_DET1_LAD2_CH2.append([base_time+2.048-8.196, int(tbdata[i][437])])
                SA_DET1_LAD2_CH2.append([base_time+2.560-8.196, int(tbdata[i][461])])
                SA_DET1_LAD2_CH2.append([base_time+3.072-8.196, int(tbdata[i][485])])
                SA_DET1_LAD2_CH2.append([base_time+3.584-8.196, int(tbdata[i][509])])
                SA_DET1_LAD2_CH2.append([base_time+4.096-8.196, int(tbdata[i][533])])
                SA_DET1_LAD2_CH2.append([base_time+4.608-8.196, int(tbdata[i][557])])
                SA_DET1_LAD2_CH2.append([base_time+5.120-8.196, int(tbdata[i][581])])
                SA_DET1_LAD2_CH2.append([base_time+5.632-8.196, int(tbdata[i][605])])
                SA_DET1_LAD2_CH2.append([base_time+6.144-8.196, int(tbdata[i][629])])
                SA_DET1_LAD2_CH2.append([base_time+6.656-8.196, int(tbdata[i][653])])
                SA_DET1_LAD2_CH2.append([base_time+7.168-8.196, int(tbdata[i][677])])
                SA_DET1_LAD2_CH2.append([base_time+7.680-8.196, int(tbdata[i][701])])

                SA_DET1_LAD2_CH3.append([base_time+0.000-8.196, int(tbdata[i][342])])
                SA_DET1_LAD2_CH3.append([base_time+0.512-8.196, int(tbdata[i][366])])
                SA_DET1_LAD2_CH3.append([base_time+1.024-8.196, int(tbdata[i][390])])
                SA_DET1_LAD2_CH3.append([base_time+1.536-8.196, int(tbdata[i][414])])
                SA_DET1_LAD2_CH3.append([base_time+2.048-8.196, int(tbdata[i][438])])
                SA_DET1_LAD2_CH3.append([base_time+2.560-8.196, int(tbdata[i][462])])
                SA_DET1_LAD2_CH3.append([base_time+3.072-8.196, int(tbdata[i][486])])
                SA_DET1_LAD2_CH3.append([base_time+3.584-8.196, int(tbdata[i][510])])
                SA_DET1_LAD2_CH3.append([base_time+4.096-8.196, int(tbdata[i][534])])
                SA_DET1_LAD2_CH3.append([base_time+4.608-8.196, int(tbdata[i][558])])
                SA_DET1_LAD2_CH3.append([base_time+5.120-8.196, int(tbdata[i][582])])
                SA_DET1_LAD2_CH3.append([base_time+5.632-8.196, int(tbdata[i][606])])
                SA_DET1_LAD2_CH3.append([base_time+6.144-8.196, int(tbdata[i][630])])
                SA_DET1_LAD2_CH3.append([base_time+6.656-8.196, int(tbdata[i][654])])
                SA_DET1_LAD2_CH3.append([base_time+7.168-8.196, int(tbdata[i][678])])
                SA_DET1_LAD2_CH3.append([base_time+7.680-8.196, int(tbdata[i][702])])

                SA_DET2_LAD1_CH1.append([base_time+0.000-8.196, int(tbdata[i][343])])
                SA_DET2_LAD1_CH1.append([base_time+0.512-8.196, int(tbdata[i][367])])
                SA_DET2_LAD1_CH1.append([base_time+1.024-8.196, int(tbdata[i][391])])
                SA_DET2_LAD1_CH1.append([base_time+1.536-8.196, int(tbdata[i][415])])
                SA_DET2_LAD1_CH1.append([base_time+2.048-8.196, int(tbdata[i][439])])
                SA_DET2_LAD1_CH1.append([base_time+2.560-8.196, int(tbdata[i][463])])
                SA_DET2_LAD1_CH1.append([base_time+3.072-8.196, int(tbdata[i][487])])
                SA_DET2_LAD1_CH1.append([base_time+3.584-8.196, int(tbdata[i][511])])
                SA_DET2_LAD1_CH1.append([base_time+4.096-8.196, int(tbdata[i][535])])
                SA_DET2_LAD1_CH1.append([base_time+4.608-8.196, int(tbdata[i][559])])
                SA_DET2_LAD1_CH1.append([base_time+5.120-8.196, int(tbdata[i][583])])
                SA_DET2_LAD1_CH1.append([base_time+5.632-8.196, int(tbdata[i][607])])
                SA_DET2_LAD1_CH1.append([base_time+6.144-8.196, int(tbdata[i][631])])
                SA_DET2_LAD1_CH1.append([base_time+6.656-8.196, int(tbdata[i][655])])
                SA_DET2_LAD1_CH1.append([base_time+7.168-8.196, int(tbdata[i][679])])
                SA_DET2_LAD1_CH1.append([base_time+7.680-8.196, int(tbdata[i][703])])

                SA_DET2_LAD1_CH2.append([base_time+0.000-8.196, int(tbdata[i][344])])
                SA_DET2_LAD1_CH2.append([base_time+0.512-8.196, int(tbdata[i][368])])
                SA_DET2_LAD1_CH2.append([base_time+1.024-8.196, int(tbdata[i][392])])
                SA_DET2_LAD1_CH2.append([base_time+1.536-8.196, int(tbdata[i][416])])
                SA_DET2_LAD1_CH2.append([base_time+2.048-8.196, int(tbdata[i][440])])
                SA_DET2_LAD1_CH2.append([base_time+2.560-8.196, int(tbdata[i][464])])
                SA_DET2_LAD1_CH2.append([base_time+3.072-8.196, int(tbdata[i][488])])
                SA_DET2_LAD1_CH2.append([base_time+3.584-8.196, int(tbdata[i][512])])
                SA_DET2_LAD1_CH2.append([base_time+4.096-8.196, int(tbdata[i][536])])
                SA_DET2_LAD1_CH2.append([base_time+4.608-8.196, int(tbdata[i][560])])
                SA_DET2_LAD1_CH2.append([base_time+5.120-8.196, int(tbdata[i][584])])
                SA_DET2_LAD1_CH2.append([base_time+5.632-8.196, int(tbdata[i][608])])
                SA_DET2_LAD1_CH2.append([base_time+6.144-8.196, int(tbdata[i][632])])
                SA_DET2_LAD1_CH2.append([base_time+6.656-8.196, int(tbdata[i][656])])
                SA_DET2_LAD1_CH2.append([base_time+7.168-8.196, int(tbdata[i][680])])
                SA_DET2_LAD1_CH2.append([base_time+7.680-8.196, int(tbdata[i][704])])

                SA_DET2_LAD1_CH3.append([base_time+0.000-8.196, int(tbdata[i][345])])
                SA_DET2_LAD1_CH3.append([base_time+0.512-8.196, int(tbdata[i][369])])
                SA_DET2_LAD1_CH3.append([base_time+1.024-8.196, int(tbdata[i][393])])
                SA_DET2_LAD1_CH3.append([base_time+1.536-8.196, int(tbdata[i][417])])
                SA_DET2_LAD1_CH3.append([base_time+2.048-8.196, int(tbdata[i][441])])
                SA_DET2_LAD1_CH3.append([base_time+2.560-8.196, int(tbdata[i][465])])
                SA_DET2_LAD1_CH3.append([base_time+3.072-8.196, int(tbdata[i][489])])
                SA_DET2_LAD1_CH3.append([base_time+3.584-8.196, int(tbdata[i][513])])
                SA_DET2_LAD1_CH3.append([base_time+4.096-8.196, int(tbdata[i][537])])
                SA_DET2_LAD1_CH3.append([base_time+4.608-8.196, int(tbdata[i][561])])
                SA_DET2_LAD1_CH3.append([base_time+5.120-8.196, int(tbdata[i][585])])
                SA_DET2_LAD1_CH3.append([base_time+5.632-8.196, int(tbdata[i][609])])
                SA_DET2_LAD1_CH3.append([base_time+6.144-8.196, int(tbdata[i][633])])
                SA_DET2_LAD1_CH3.append([base_time+6.656-8.196, int(tbdata[i][657])])
                SA_DET2_LAD1_CH3.append([base_time+7.168-8.196, int(tbdata[i][681])])
                SA_DET2_LAD1_CH3.append([base_time+7.680-8.196, int(tbdata[i][705])])

                SA_DET2_LAD2_CH1.append([base_time+0.000-8.196, int(tbdata[i][346])])
                SA_DET2_LAD2_CH1.append([base_time+0.512-8.196, int(tbdata[i][370])])
                SA_DET2_LAD2_CH1.append([base_time+1.024-8.196, int(tbdata[i][394])])
                SA_DET2_LAD2_CH1.append([base_time+1.536-8.196, int(tbdata[i][418])])
                SA_DET2_LAD2_CH1.append([base_time+2.048-8.196, int(tbdata[i][442])])
                SA_DET2_LAD2_CH1.append([base_time+2.560-8.196, int(tbdata[i][466])])
                SA_DET2_LAD2_CH1.append([base_time+3.072-8.196, int(tbdata[i][490])])
                SA_DET2_LAD2_CH1.append([base_time+3.584-8.196, int(tbdata[i][514])])
                SA_DET2_LAD2_CH1.append([base_time+4.096-8.196, int(tbdata[i][538])])
                SA_DET2_LAD2_CH1.append([base_time+4.608-8.196, int(tbdata[i][562])])
                SA_DET2_LAD2_CH1.append([base_time+5.120-8.196, int(tbdata[i][586])])
                SA_DET2_LAD2_CH1.append([base_time+5.632-8.196, int(tbdata[i][610])])
                SA_DET2_LAD2_CH1.append([base_time+6.144-8.196, int(tbdata[i][634])])
                SA_DET2_LAD2_CH1.append([base_time+6.656-8.196, int(tbdata[i][658])])
                SA_DET2_LAD2_CH1.append([base_time+7.168-8.196, int(tbdata[i][682])])
                SA_DET2_LAD2_CH1.append([base_time+7.680-8.196, int(tbdata[i][706])])

                SA_DET2_LAD2_CH2.append([base_time+0.000-8.196, int(tbdata[i][347])])
                SA_DET2_LAD2_CH2.append([base_time+0.512-8.196, int(tbdata[i][371])])
                SA_DET2_LAD2_CH2.append([base_time+1.024-8.196, int(tbdata[i][395])])
                SA_DET2_LAD2_CH2.append([base_time+1.536-8.196, int(tbdata[i][419])])
                SA_DET2_LAD2_CH2.append([base_time+2.048-8.196, int(tbdata[i][443])])
                SA_DET2_LAD2_CH2.append([base_time+2.560-8.196, int(tbdata[i][467])])
                SA_DET2_LAD2_CH2.append([base_time+3.072-8.196, int(tbdata[i][491])])
                SA_DET2_LAD2_CH2.append([base_time+3.584-8.196, int(tbdata[i][515])])
                SA_DET2_LAD2_CH2.append([base_time+4.096-8.196, int(tbdata[i][539])])
                SA_DET2_LAD2_CH2.append([base_time+4.608-8.196, int(tbdata[i][563])])
                SA_DET2_LAD2_CH2.append([base_time+5.120-8.196, int(tbdata[i][587])])
                SA_DET2_LAD2_CH2.append([base_time+5.632-8.196, int(tbdata[i][611])])
                SA_DET2_LAD2_CH2.append([base_time+6.144-8.196, int(tbdata[i][635])])
                SA_DET2_LAD2_CH2.append([base_time+6.656-8.196, int(tbdata[i][659])])
                SA_DET2_LAD2_CH2.append([base_time+7.168-8.196, int(tbdata[i][683])])
                SA_DET2_LAD2_CH2.append([base_time+7.680-8.196, int(tbdata[i][707])])

                SA_DET2_LAD2_CH3.append([base_time+0.000-8.196, int(tbdata[i][348])])
                SA_DET2_LAD2_CH3.append([base_time+0.512-8.196, int(tbdata[i][372])])
                SA_DET2_LAD2_CH3.append([base_time+1.024-8.196, int(tbdata[i][396])])
                SA_DET2_LAD2_CH3.append([base_time+1.536-8.196, int(tbdata[i][420])])
                SA_DET2_LAD2_CH3.append([base_time+2.048-8.196, int(tbdata[i][444])])
                SA_DET2_LAD2_CH3.append([base_time+2.560-8.196, int(tbdata[i][468])])
                SA_DET2_LAD2_CH3.append([base_time+3.072-8.196, int(tbdata[i][492])])
                SA_DET2_LAD2_CH3.append([base_time+3.584-8.196, int(tbdata[i][516])])
                SA_DET2_LAD2_CH3.append([base_time+4.096-8.196, int(tbdata[i][540])])
                SA_DET2_LAD2_CH3.append([base_time+4.608-8.196, int(tbdata[i][564])])
                SA_DET2_LAD2_CH3.append([base_time+5.120-8.196, int(tbdata[i][588])])
                SA_DET2_LAD2_CH3.append([base_time+5.632-8.196, int(tbdata[i][612])])
                SA_DET2_LAD2_CH3.append([base_time+6.144-8.196, int(tbdata[i][636])])
                SA_DET2_LAD2_CH3.append([base_time+6.656-8.196, int(tbdata[i][660])])
                SA_DET2_LAD2_CH3.append([base_time+7.168-8.196, int(tbdata[i][684])])
                SA_DET2_LAD2_CH3.append([base_time+7.680-8.196, int(tbdata[i][708])])

                SA_DET3_LAD1_CH1.append([base_time+0.000-8.196, int(tbdata[i][349])])
                SA_DET3_LAD1_CH1.append([base_time+0.512-8.196, int(tbdata[i][373])])
                SA_DET3_LAD1_CH1.append([base_time+1.024-8.196, int(tbdata[i][397])])
                SA_DET3_LAD1_CH1.append([base_time+1.536-8.196, int(tbdata[i][421])])
                SA_DET3_LAD1_CH1.append([base_time+2.048-8.196, int(tbdata[i][445])])
                SA_DET3_LAD1_CH1.append([base_time+2.560-8.196, int(tbdata[i][469])])
                SA_DET3_LAD1_CH1.append([base_time+3.072-8.196, int(tbdata[i][493])])
                SA_DET3_LAD1_CH1.append([base_time+3.584-8.196, int(tbdata[i][517])])
                SA_DET3_LAD1_CH1.append([base_time+4.096-8.196, int(tbdata[i][541])])
                SA_DET3_LAD1_CH1.append([base_time+4.608-8.196, int(tbdata[i][565])])
                SA_DET3_LAD1_CH1.append([base_time+5.120-8.196, int(tbdata[i][589])])
                SA_DET3_LAD1_CH1.append([base_time+5.632-8.196, int(tbdata[i][613])])
                SA_DET3_LAD1_CH1.append([base_time+6.144-8.196, int(tbdata[i][637])])
                SA_DET3_LAD1_CH1.append([base_time+6.656-8.196, int(tbdata[i][661])])
                SA_DET3_LAD1_CH1.append([base_time+7.168-8.196, int(tbdata[i][685])])
                SA_DET3_LAD1_CH1.append([base_time+7.680-8.196, int(tbdata[i][709])])

                SA_DET3_LAD1_CH2.append([base_time+0.000-8.196, int(tbdata[i][350])])
                SA_DET3_LAD1_CH2.append([base_time+0.512-8.196, int(tbdata[i][374])])
                SA_DET3_LAD1_CH2.append([base_time+1.024-8.196, int(tbdata[i][398])])
                SA_DET3_LAD1_CH2.append([base_time+1.536-8.196, int(tbdata[i][422])])
                SA_DET3_LAD1_CH2.append([base_time+2.048-8.196, int(tbdata[i][446])])
                SA_DET3_LAD1_CH2.append([base_time+2.560-8.196, int(tbdata[i][470])])
                SA_DET3_LAD1_CH2.append([base_time+3.072-8.196, int(tbdata[i][494])])
                SA_DET3_LAD1_CH2.append([base_time+3.584-8.196, int(tbdata[i][518])])
                SA_DET3_LAD1_CH2.append([base_time+4.096-8.196, int(tbdata[i][542])])
                SA_DET3_LAD1_CH2.append([base_time+4.608-8.196, int(tbdata[i][566])])
                SA_DET3_LAD1_CH2.append([base_time+5.120-8.196, int(tbdata[i][590])])
                SA_DET3_LAD1_CH2.append([base_time+5.632-8.196, int(tbdata[i][614])])
                SA_DET3_LAD1_CH2.append([base_time+6.144-8.196, int(tbdata[i][638])])
                SA_DET3_LAD1_CH2.append([base_time+6.656-8.196, int(tbdata[i][662])])
                SA_DET3_LAD1_CH2.append([base_time+7.168-8.196, int(tbdata[i][686])])
                SA_DET3_LAD1_CH2.append([base_time+7.680-8.196, int(tbdata[i][710])])

                SA_DET3_LAD1_CH3.append([base_time+0.000-8.196, int(tbdata[i][351])])
                SA_DET3_LAD1_CH3.append([base_time+0.512-8.196, int(tbdata[i][375])])
                SA_DET3_LAD1_CH3.append([base_time+1.024-8.196, int(tbdata[i][399])])
                SA_DET3_LAD1_CH3.append([base_time+1.536-8.196, int(tbdata[i][423])])
                SA_DET3_LAD1_CH3.append([base_time+2.048-8.196, int(tbdata[i][447])])
                SA_DET3_LAD1_CH3.append([base_time+2.560-8.196, int(tbdata[i][471])])
                SA_DET3_LAD1_CH3.append([base_time+3.072-8.196, int(tbdata[i][495])])
                SA_DET3_LAD1_CH3.append([base_time+3.584-8.196, int(tbdata[i][519])])
                SA_DET3_LAD1_CH3.append([base_time+4.096-8.196, int(tbdata[i][543])])
                SA_DET3_LAD1_CH3.append([base_time+4.608-8.196, int(tbdata[i][567])])
                SA_DET3_LAD1_CH3.append([base_time+5.120-8.196, int(tbdata[i][591])])
                SA_DET3_LAD1_CH3.append([base_time+5.632-8.196, int(tbdata[i][615])])
                SA_DET3_LAD1_CH3.append([base_time+6.144-8.196, int(tbdata[i][639])])
                SA_DET3_LAD1_CH3.append([base_time+6.656-8.196, int(tbdata[i][663])])
                SA_DET3_LAD1_CH3.append([base_time+7.168-8.196, int(tbdata[i][687])])
                SA_DET3_LAD1_CH3.append([base_time+7.680-8.196, int(tbdata[i][711])])

                SA_DET3_LAD2_CH1.append([base_time+0.000-8.196, int(tbdata[i][352])])
                SA_DET3_LAD2_CH1.append([base_time+0.512-8.196, int(tbdata[i][376])])
                SA_DET3_LAD2_CH1.append([base_time+1.024-8.196, int(tbdata[i][400])])
                SA_DET3_LAD2_CH1.append([base_time+1.536-8.196, int(tbdata[i][424])])
                SA_DET3_LAD2_CH1.append([base_time+2.048-8.196, int(tbdata[i][448])])
                SA_DET3_LAD2_CH1.append([base_time+2.560-8.196, int(tbdata[i][472])])
                SA_DET3_LAD2_CH1.append([base_time+3.072-8.196, int(tbdata[i][496])])
                SA_DET3_LAD2_CH1.append([base_time+3.584-8.196, int(tbdata[i][520])])
                SA_DET3_LAD2_CH1.append([base_time+4.096-8.196, int(tbdata[i][544])])
                SA_DET3_LAD2_CH1.append([base_time+4.608-8.196, int(tbdata[i][568])])
                SA_DET3_LAD2_CH1.append([base_time+5.120-8.196, int(tbdata[i][592])])
                SA_DET3_LAD2_CH1.append([base_time+5.632-8.196, int(tbdata[i][616])])
                SA_DET3_LAD2_CH1.append([base_time+6.144-8.196, int(tbdata[i][640])])
                SA_DET3_LAD2_CH1.append([base_time+6.656-8.196, int(tbdata[i][664])])
                SA_DET3_LAD2_CH1.append([base_time+7.168-8.196, int(tbdata[i][688])])
                SA_DET3_LAD2_CH1.append([base_time+7.680-8.196, int(tbdata[i][712])])

                SA_DET3_LAD2_CH2.append([base_time+0.000-8.196, int(tbdata[i][353])])
                SA_DET3_LAD2_CH2.append([base_time+0.512-8.196, int(tbdata[i][377])])
                SA_DET3_LAD2_CH2.append([base_time+1.024-8.196, int(tbdata[i][401])])
                SA_DET3_LAD2_CH2.append([base_time+1.536-8.196, int(tbdata[i][425])])
                SA_DET3_LAD2_CH2.append([base_time+2.048-8.196, int(tbdata[i][449])])
                SA_DET3_LAD2_CH2.append([base_time+2.560-8.196, int(tbdata[i][473])])
                SA_DET3_LAD2_CH2.append([base_time+3.072-8.196, int(tbdata[i][497])])
                SA_DET3_LAD2_CH2.append([base_time+3.584-8.196, int(tbdata[i][521])])
                SA_DET3_LAD2_CH2.append([base_time+4.096-8.196, int(tbdata[i][545])])
                SA_DET3_LAD2_CH2.append([base_time+4.608-8.196, int(tbdata[i][569])])
                SA_DET3_LAD2_CH2.append([base_time+5.120-8.196, int(tbdata[i][593])])
                SA_DET3_LAD2_CH2.append([base_time+5.632-8.196, int(tbdata[i][617])])
                SA_DET3_LAD2_CH2.append([base_time+6.144-8.196, int(tbdata[i][641])])
                SA_DET3_LAD2_CH2.append([base_time+6.656-8.196, int(tbdata[i][665])])
                SA_DET3_LAD2_CH2.append([base_time+7.168-8.196, int(tbdata[i][689])])
                SA_DET3_LAD2_CH2.append([base_time+7.680-8.196, int(tbdata[i][713])])

                SA_DET3_LAD2_CH3.append([base_time+0.000-8.196, int(tbdata[i][354])])
                SA_DET3_LAD2_CH3.append([base_time+0.512-8.196, int(tbdata[i][378])])
                SA_DET3_LAD2_CH3.append([base_time+1.024-8.196, int(tbdata[i][402])])
                SA_DET3_LAD2_CH3.append([base_time+1.536-8.196, int(tbdata[i][426])])
                SA_DET3_LAD2_CH3.append([base_time+2.048-8.196, int(tbdata[i][450])])
                SA_DET3_LAD2_CH3.append([base_time+2.560-8.196, int(tbdata[i][474])])
                SA_DET3_LAD2_CH3.append([base_time+3.072-8.196, int(tbdata[i][498])])
                SA_DET3_LAD2_CH3.append([base_time+3.584-8.196, int(tbdata[i][522])])
                SA_DET3_LAD2_CH3.append([base_time+4.096-8.196, int(tbdata[i][546])])
                SA_DET3_LAD2_CH3.append([base_time+4.608-8.196, int(tbdata[i][570])])
                SA_DET3_LAD2_CH3.append([base_time+5.120-8.196, int(tbdata[i][594])])
                SA_DET3_LAD2_CH3.append([base_time+5.632-8.196, int(tbdata[i][618])])
                SA_DET3_LAD2_CH3.append([base_time+6.144-8.196, int(tbdata[i][642])])
                SA_DET3_LAD2_CH3.append([base_time+6.656-8.196, int(tbdata[i][666])])
                SA_DET3_LAD2_CH3.append([base_time+7.168-8.196, int(tbdata[i][690])])
                SA_DET3_LAD2_CH3.append([base_time+7.680-8.196, int(tbdata[i][714])])

                SA_DET4_LAD1_CH1.append([base_time+0.000-8.196, int(tbdata[i][355])])
                SA_DET4_LAD1_CH1.append([base_time+0.512-8.196, int(tbdata[i][379])])
                SA_DET4_LAD1_CH1.append([base_time+1.024-8.196, int(tbdata[i][403])])
                SA_DET4_LAD1_CH1.append([base_time+1.536-8.196, int(tbdata[i][427])])
                SA_DET4_LAD1_CH1.append([base_time+2.048-8.196, int(tbdata[i][451])])
                SA_DET4_LAD1_CH1.append([base_time+2.560-8.196, int(tbdata[i][475])])
                SA_DET4_LAD1_CH1.append([base_time+3.072-8.196, int(tbdata[i][499])])
                SA_DET4_LAD1_CH1.append([base_time+3.584-8.196, int(tbdata[i][523])])
                SA_DET4_LAD1_CH1.append([base_time+4.096-8.196, int(tbdata[i][547])])
                SA_DET4_LAD1_CH1.append([base_time+4.608-8.196, int(tbdata[i][571])])
                SA_DET4_LAD1_CH1.append([base_time+5.120-8.196, int(tbdata[i][595])])
                SA_DET4_LAD1_CH1.append([base_time+5.632-8.196, int(tbdata[i][619])])
                SA_DET4_LAD1_CH1.append([base_time+6.144-8.196, int(tbdata[i][643])])
                SA_DET4_LAD1_CH1.append([base_time+6.656-8.196, int(tbdata[i][667])])
                SA_DET4_LAD1_CH1.append([base_time+7.168-8.196, int(tbdata[i][691])])
                SA_DET4_LAD1_CH1.append([base_time+7.680-8.196, int(tbdata[i][715])])

                SA_DET4_LAD1_CH2.append([base_time+0.000-8.196, int(tbdata[i][356])])
                SA_DET4_LAD1_CH2.append([base_time+0.512-8.196, int(tbdata[i][380])])
                SA_DET4_LAD1_CH2.append([base_time+1.024-8.196, int(tbdata[i][404])])
                SA_DET4_LAD1_CH2.append([base_time+1.536-8.196, int(tbdata[i][428])])
                SA_DET4_LAD1_CH2.append([base_time+2.048-8.196, int(tbdata[i][452])])
                SA_DET4_LAD1_CH2.append([base_time+2.560-8.196, int(tbdata[i][476])])
                SA_DET4_LAD1_CH2.append([base_time+3.072-8.196, int(tbdata[i][500])])
                SA_DET4_LAD1_CH2.append([base_time+3.584-8.196, int(tbdata[i][524])])
                SA_DET4_LAD1_CH2.append([base_time+4.096-8.196, int(tbdata[i][548])])
                SA_DET4_LAD1_CH2.append([base_time+4.608-8.196, int(tbdata[i][572])])
                SA_DET4_LAD1_CH2.append([base_time+5.120-8.196, int(tbdata[i][596])])
                SA_DET4_LAD1_CH2.append([base_time+5.632-8.196, int(tbdata[i][620])])
                SA_DET4_LAD1_CH2.append([base_time+6.144-8.196, int(tbdata[i][644])])
                SA_DET4_LAD1_CH2.append([base_time+6.656-8.196, int(tbdata[i][668])])
                SA_DET4_LAD1_CH2.append([base_time+7.168-8.196, int(tbdata[i][692])])
                SA_DET4_LAD1_CH2.append([base_time+7.680-8.196, int(tbdata[i][716])])

                SA_DET4_LAD1_CH3.append([base_time+0.000-8.196, int(tbdata[i][357])])
                SA_DET4_LAD1_CH3.append([base_time+0.512-8.196, int(tbdata[i][381])])
                SA_DET4_LAD1_CH3.append([base_time+1.024-8.196, int(tbdata[i][405])])
                SA_DET4_LAD1_CH3.append([base_time+1.536-8.196, int(tbdata[i][429])])
                SA_DET4_LAD1_CH3.append([base_time+2.048-8.196, int(tbdata[i][453])])
                SA_DET4_LAD1_CH3.append([base_time+2.560-8.196, int(tbdata[i][477])])
                SA_DET4_LAD1_CH3.append([base_time+3.072-8.196, int(tbdata[i][501])])
                SA_DET4_LAD1_CH3.append([base_time+3.584-8.196, int(tbdata[i][525])])
                SA_DET4_LAD1_CH3.append([base_time+4.096-8.196, int(tbdata[i][549])])
                SA_DET4_LAD1_CH3.append([base_time+4.608-8.196, int(tbdata[i][573])])
                SA_DET4_LAD1_CH3.append([base_time+5.120-8.196, int(tbdata[i][597])])
                SA_DET4_LAD1_CH3.append([base_time+5.632-8.196, int(tbdata[i][621])])
                SA_DET4_LAD1_CH3.append([base_time+6.144-8.196, int(tbdata[i][645])])
                SA_DET4_LAD1_CH3.append([base_time+6.656-8.196, int(tbdata[i][669])])
                SA_DET4_LAD1_CH3.append([base_time+7.168-8.196, int(tbdata[i][693])])
                SA_DET4_LAD1_CH3.append([base_time+7.680-8.196, int(tbdata[i][717])])

                SA_DET4_LAD2_CH1.append([base_time+0.000-8.196, int(tbdata[i][358])])
                SA_DET4_LAD2_CH1.append([base_time+0.512-8.196, int(tbdata[i][382])])
                SA_DET4_LAD2_CH1.append([base_time+1.024-8.196, int(tbdata[i][406])])
                SA_DET4_LAD2_CH1.append([base_time+1.536-8.196, int(tbdata[i][430])])
                SA_DET4_LAD2_CH1.append([base_time+2.048-8.196, int(tbdata[i][454])])
                SA_DET4_LAD2_CH1.append([base_time+2.560-8.196, int(tbdata[i][478])])
                SA_DET4_LAD2_CH1.append([base_time+3.072-8.196, int(tbdata[i][502])])
                SA_DET4_LAD2_CH1.append([base_time+3.584-8.196, int(tbdata[i][526])])
                SA_DET4_LAD2_CH1.append([base_time+4.096-8.196, int(tbdata[i][550])])
                SA_DET4_LAD2_CH1.append([base_time+4.608-8.196, int(tbdata[i][574])])
                SA_DET4_LAD2_CH1.append([base_time+5.120-8.196, int(tbdata[i][598])])
                SA_DET4_LAD2_CH1.append([base_time+5.632-8.196, int(tbdata[i][622])])
                SA_DET4_LAD2_CH1.append([base_time+6.144-8.196, int(tbdata[i][646])])
                SA_DET4_LAD2_CH1.append([base_time+6.656-8.196, int(tbdata[i][670])])
                SA_DET4_LAD2_CH1.append([base_time+7.168-8.196, int(tbdata[i][694])])
                SA_DET4_LAD2_CH1.append([base_time+7.680-8.196, int(tbdata[i][718])])

                SA_DET4_LAD2_CH2.append([base_time+0.000-8.196, int(tbdata[i][359])])
                SA_DET4_LAD2_CH2.append([base_time+0.512-8.196, int(tbdata[i][383])])
                SA_DET4_LAD2_CH2.append([base_time+1.024-8.196, int(tbdata[i][407])])
                SA_DET4_LAD2_CH2.append([base_time+1.536-8.196, int(tbdata[i][431])])
                SA_DET4_LAD2_CH2.append([base_time+2.048-8.196, int(tbdata[i][455])])
                SA_DET4_LAD2_CH2.append([base_time+2.560-8.196, int(tbdata[i][479])])
                SA_DET4_LAD2_CH2.append([base_time+3.072-8.196, int(tbdata[i][503])])
                SA_DET4_LAD2_CH2.append([base_time+3.584-8.196, int(tbdata[i][527])])
                SA_DET4_LAD2_CH2.append([base_time+4.096-8.196, int(tbdata[i][551])])
                SA_DET4_LAD2_CH2.append([base_time+4.608-8.196, int(tbdata[i][575])])
                SA_DET4_LAD2_CH2.append([base_time+5.120-8.196, int(tbdata[i][599])])
                SA_DET4_LAD2_CH2.append([base_time+5.632-8.196, int(tbdata[i][623])])
                SA_DET4_LAD2_CH2.append([base_time+6.144-8.196, int(tbdata[i][647])])
                SA_DET4_LAD2_CH2.append([base_time+6.656-8.196, int(tbdata[i][671])])
                SA_DET4_LAD2_CH2.append([base_time+7.168-8.196, int(tbdata[i][695])])
                SA_DET4_LAD2_CH2.append([base_time+7.680-8.196, int(tbdata[i][719])])

                SA_DET4_LAD2_CH3.append([base_time+0.000-8.196, int(tbdata[i][360])])
                SA_DET4_LAD2_CH3.append([base_time+0.512-8.196, int(tbdata[i][384])])
                SA_DET4_LAD2_CH3.append([base_time+1.024-8.196, int(tbdata[i][408])])
                SA_DET4_LAD2_CH3.append([base_time+1.536-8.196, int(tbdata[i][432])])
                SA_DET4_LAD2_CH3.append([base_time+2.048-8.196, int(tbdata[i][456])])
                SA_DET4_LAD2_CH3.append([base_time+2.560-8.196, int(tbdata[i][480])])
                SA_DET4_LAD2_CH3.append([base_time+3.072-8.196, int(tbdata[i][504])])
                SA_DET4_LAD2_CH3.append([base_time+3.584-8.196, int(tbdata[i][528])])
                SA_DET4_LAD2_CH3.append([base_time+4.096-8.196, int(tbdata[i][552])])
                SA_DET4_LAD2_CH3.append([base_time+4.608-8.196, int(tbdata[i][576])])
                SA_DET4_LAD2_CH3.append([base_time+5.120-8.196, int(tbdata[i][600])])
                SA_DET4_LAD2_CH3.append([base_time+5.632-8.196, int(tbdata[i][624])])
                SA_DET4_LAD2_CH3.append([base_time+6.144-8.196, int(tbdata[i][648])])
                SA_DET4_LAD2_CH3.append([base_time+6.656-8.196, int(tbdata[i][672])])
                SA_DET4_LAD2_CH3.append([base_time+7.168-8.196, int(tbdata[i][696])])
                SA_DET4_LAD2_CH3.append([base_time+7.680-8.196, int(tbdata[i][720])])

            #################
            # CREATE TABLES #
            #################
            self.logger.info(f"Computing Ratemeters Time Series...")
            # All Data was read.
            # Now sum all the contributions into 1 array per instrument, merging all channels.
            
            # SILICON TRACKER
            GRID = Table()
            GRID['OBT'] = [row[0] for row in GRID_1X]
            GRID_counts = []
            for j in range(len(GRID_1X)):
                GRID_counts.append(
                    [GRID_1X[j][1]+GRID_2X[j][1]+GRID_3X[j][1]+GRID_4X[j][1]+GRID_5X[j][1]+GRID_6X[j][1]+
                     GRID_1Z[j][1]+GRID_2Z[j][1]+GRID_3Z[j][1]+GRID_4Z[j][1]+GRID_5Z[j][1]+GRID_6Z[j][1]
                    ])
            GRID['COUNTS'] = np.array(GRID_counts).flatten()

            # ANTI-COINCIDENCES
            AC_SIDE0 = np.array(AC_SIDE0)
            AC_SIDE1 = np.array(AC_SIDE1)
            AC_SIDE2 = np.array(AC_SIDE2)
            AC_SIDE3 = np.array(AC_SIDE3)
            AC_SIDE4 = np.array(AC_SIDE4)
            
            AC_SIDE0 = Table([AC_SIDE0[:,0],AC_SIDE0[:,1]], names=('OBT','COUNTS'), dtype=('f8','i4'))
            AC_SIDE1 = Table([AC_SIDE1[:,0],AC_SIDE1[:,1]], names=('OBT','COUNTS'), dtype=('f8','i4'))
            AC_SIDE2 = Table([AC_SIDE2[:,0],AC_SIDE2[:,1]], names=('OBT','COUNTS'), dtype=('f8','i4'))
            AC_SIDE3 = Table([AC_SIDE3[:,0],AC_SIDE3[:,1]], names=('OBT','COUNTS'), dtype=('f8','i4'))
            AC_SIDE4 = Table([AC_SIDE4[:,0],AC_SIDE4[:,1]], names=('OBT','COUNTS'), dtype=('f8','i4'))
            
            # MINI-CALORIMETER 
            MCAL = Table()
            MCAL['OBT'] = [row[0] for row in MCAL_X_CH01]
            MCAL_counts = []
            for j in range(len(MCAL_X_CH01)):
                MCAL_counts.append(
                    [MCAL_X_CH01[j][1]+MCAL_X_CH02[j][1]+MCAL_X_CH03[j][1]+MCAL_X_CH04[j][1]+MCAL_X_CH05[j][1]+MCAL_X_CH06[j][1]+MCAL_X_CH07[j][1]+MCAL_X_CH08[j][1]+MCAL_X_CH09[j][1]+MCAL_X_CH10[j][1]+MCAL_X_CH11[j][1]+
                     MCAL_Z_CH01[j][1]+MCAL_Z_CH02[j][1]+MCAL_Z_CH03[j][1]+MCAL_Z_CH04[j][1]+MCAL_Z_CH05[j][1]+MCAL_Z_CH06[j][1]+MCAL_Z_CH07[j][1]+MCAL_Z_CH08[j][1]+MCAL_Z_CH09[j][1]+MCAL_Z_CH10[j][1]+MCAL_Z_CH11[j][1]
                     ])
            MCAL['COUNTS'] = np.array(MCAL_counts).flatten()

            # SUPER-AGILE
            SA = Table()
            SA['OBT'] = [row[0] for row in SA_DET1_LAD1_CH1]
            SA_counts = []
            for j in range(len(SA_DET1_LAD1_CH1)):
                SA_counts.append(
                    [SA_DET1_LAD1_CH1[j][1]+SA_DET1_LAD1_CH2[j][1]+SA_DET1_LAD1_CH3[j][1]+
                     SA_DET1_LAD2_CH1[j][1]+SA_DET1_LAD2_CH2[j][1]+SA_DET1_LAD2_CH3[j][1]+
                     SA_DET2_LAD1_CH1[j][1]+SA_DET2_LAD1_CH2[j][1]+SA_DET2_LAD1_CH3[j][1]+
                     SA_DET2_LAD2_CH1[j][1]+SA_DET2_LAD2_CH2[j][1]+SA_DET2_LAD2_CH3[j][1]+
                     SA_DET3_LAD1_CH1[j][1]+SA_DET3_LAD1_CH2[j][1]+SA_DET3_LAD1_CH3[j][1]+
                     SA_DET3_LAD2_CH1[j][1]+SA_DET3_LAD2_CH2[j][1]+SA_DET3_LAD2_CH3[j][1]+
                     SA_DET4_LAD1_CH1[j][1]+SA_DET4_LAD1_CH2[j][1]+SA_DET4_LAD1_CH3[j][1]+
                     SA_DET4_LAD2_CH1[j][1]+SA_DET4_LAD2_CH2[j][1]+SA_DET4_LAD2_CH3[j][1]
                    ])
            SA['COUNTS'] = np.array(SA_counts).flatten()

            #################################################
            # APPLY FFT DETRENDING OF BACKGROUND MODULATION #
            #################################################
            GRID['COUNTS_D']     = self._detrendData(    GRID, sampling=0.512, frequency_cut_range=(1.0E-4,1.0E-2))
            SA['COUNTS_D']       = self._detrendData(      SA, sampling=0.512, frequency_cut_range=(1.0E-4,1.0E-2))
            MCAL['COUNTS_D']     = self._detrendData(    MCAL, sampling=1.024, frequency_cut_range=(1.0E-5,3.0E-2))
            AC_SIDE0['COUNTS_D'] = self._detrendData(AC_SIDE0, sampling=1.024, frequency_cut_range=(1.0E-5,3.0E-2))
            AC_SIDE1['COUNTS_D'] = self._detrendData(AC_SIDE1, sampling=1.024, frequency_cut_range=(1.0E-5,3.0E-2))
            AC_SIDE2['COUNTS_D'] = self._detrendData(AC_SIDE2, sampling=1.024, frequency_cut_range=(1.0E-5,3.0E-2))
            AC_SIDE3['COUNTS_D'] = self._detrendData(AC_SIDE3, sampling=1.024, frequency_cut_range=(1.0E-5,3.0E-2))
            AC_SIDE4['COUNTS_D'] = self._detrendData(AC_SIDE4, sampling=1.024, frequency_cut_range=(1.0E-5,3.0E-2))

            # Sort by Time
            SA.sort('OBT')
            AC_SIDE0.sort('OBT')
            AC_SIDE1.sort('OBT')
            AC_SIDE2.sort('OBT')
            AC_SIDE3.sort('OBT')
            AC_SIDE4.sort('OBT')
            MCAL.sort('OBT')
            GRID.sort('OBT')

            ###########################
            # CREATE RATEMETERS FILES #
            ###########################
            if writeFiles:
                self.logger.info(f"Writing Ratemeters Time Series in: {self.outdir}")
                output_directory = Path(self.outdir).absolute().joinpath("rm")
                output_directory.mkdir(exist_ok=True, parents=True)
                
                GRID.write(   output_directory.joinpath('RM-GRID_LC.txt'), format='ascii', delimiter=' ', overwrite=True)
                SA.write(       output_directory.joinpath('RM-SA_LC.txt'), format='ascii', delimiter=' ', overwrite=True)
                MCAL.write(   output_directory.joinpath('RM-MCAL_LC.txt'), format='ascii', delimiter=' ', overwrite=True)
                AC_SIDE0.write(output_directory.joinpath('RM-AC0_LC.txt'), format='ascii', delimiter=' ', overwrite=True)
                AC_SIDE1.write(output_directory.joinpath('RM-AC1_LC.txt'), format='ascii', delimiter=' ', overwrite=True)
                AC_SIDE2.write(output_directory.joinpath('RM-AC2_LC.txt'), format='ascii', delimiter=' ', overwrite=True)
                AC_SIDE3.write(output_directory.joinpath('RM-AC3_LC.txt'), format='ascii', delimiter=' ', overwrite=True)
                AC_SIDE4.write(output_directory.joinpath('RM-AC4_LC.txt'), format='ascii', delimiter=' ', overwrite=True)
                
        # Return
        ratemetersTables = {"GRID":GRID,"MCAL":MCAL,"SA":SA,"AC0":AC_SIDE0,"AC1":AC_SIDE1,"AC2":AC_SIDE2,"AC3":AC_SIDE3,"AC4":AC_SIDE4}
        self._ratemetersTables = ratemetersTables
        self.logger.info(f"Done.")
        return ratemetersTables
    
    @property
    def ratemetersTables(self):
        return self._ratemetersTables
    
    def plotRatemeters(self, plotInstruments=["3RM"], plotRange=(-100, 100), useDetrendedData=True):
        """Plot Ratemeters Light Curves.

        Args:
            plotInstruments (list of str): Keys of the instruments to plot (including "2RM", "3RM", "8RM"). Defaults to ["3RM"].
            plotRange (tuple(float, float)): Time limits of the plots, in seconds relative to T0.
            useDetrendedData (bool): If True, plot detrended counts, otherwise plot raw counts. Defaults to True.

        Returns:
            plots (list(str) or None): Plot output paths.
        """
        data_flag = "D" if useDetrendedData else "ND"
        plots = []
        # Plot the chosen instruments
        if "2RM" in plotInstruments:
            instrument_list = ["AC0","MCAL"]
            filePath = Path(self.outdir).absolute().joinpath(f"plots/ratemeters_{data_flag}_2RM.png")
            plot = self.plottingUtils.plotRatemeters(self._ratemetersTables,instrument_list,self.config.getOptionValue("T0"),plotRange,useDetrendedData,filePath)
            plots.append(plot)
        if "3RM" in plotInstruments:
            instrument_list = ["SA","AC0","MCAL"]
            filePath = Path(self.outdir).absolute().joinpath(f"plots/ratemeters_{data_flag}_3RM.png")
            plot = self.plottingUtils.plotRatemeters(self._ratemetersTables,instrument_list,self.config.getOptionValue("T0"),plotRange,useDetrendedData,filePath)
            plots.append(plot)
        if "8RM" in plotInstruments:
            instrument_list = ["SA","GRID","AC0","AC1","AC2","AC3","AC4","MCAL"]
            filePath = Path(self.outdir).absolute().joinpath(f"plots/ratemeters_{data_flag}_8RM.png")
            plot = self.plottingUtils.plotRatemeters(self._ratemetersTables,instrument_list,self.config.getOptionValue("T0"),plotRange,useDetrendedData,filePath)
            plots.append(plot)

        # Requested Instruments
        # Remove "2RM", "3RM", "8RM".
        instrument_list = [item for item in plotInstruments if item not in ("2RM","3RM","8RM")]
        if len(instrument_list)==0:
            return plots
        fileName = f"ratemeters_{data_flag}_"+"_".join(instrument_list)+".png"
        filePath = Path(self.outdir).absolute().joinpath(f"plots/{fileName}")
        
        plot = self.plottingUtils.plotRatemeters(self._ratemetersTables,instrument_list,self.config.getOptionValue("T0"),plotRange,useDetrendedData,filePath)
        plots.append(plot)
        
        return plots


    def _analyseTable(self, data_table, backgroundRange, signalRange, useDetrendedData=True):
        """Analyse the Burst in a given table.

        Args:
            data_table (astropy.table.Table): Ratemeters Light Curve Table.
            backgroundRange (tuple(float, float)): Time range for background selection, in seconds relative to T0.
            signalRange (tuple(float, float)): Time range for signal selection, in seconds relative to T0.
            useDetrendedData (bool): If True, use detrended data.
        
        Return:
            results (dict): Dictionary with ON and OFF counts and time interval. Also includes background rate and Li&Ma significance.
        """
        # Get T0
        T0 = self.getOption("T0")
        
        time = data_table['OBT'].data - T0
        counts = data_table['COUNTS_D'].data if useDetrendedData else data_table['COUNTS'].data
        
        # Evaluate Background
        mask_bkg = (time>=backgroundRange[0])&(time<=backgroundRange[1])
        time_bkg = time[mask_bkg]
        counts_bkg = counts[mask_bkg]
        
        N_OFF = np.round(np.sum(counts_bkg)).astype(int) # Round is needed for detrended data
        t_OFF = np.round(time_bkg[-1]-time_bkg[0],3)
        
        # Evaluate Signal
        mask_sig = (time>=signalRange[0])&(time<=signalRange[1])
        time_sig = time[mask_sig]
        counts_sig = counts[mask_sig]
        
        N_ON = np.round(np.sum(counts_sig)).astype(int)
        t_ON = np.round(time_sig[-1]-time_sig[0],3)
        
        # Collect Results
        R_BKG = N_OFF/t_OFF
        li_ma = AstroUtils.li_ma(N_ON, N_OFF, t_ON / t_OFF)
        results = {"t_ON":t_ON,"N_ON":N_ON,"t_OFF":t_OFF,"N_OFF":N_OFF,"R_BKG":np.round(R_BKG,3),"lima":np.round(li_ma,3)}
        
        return results


    def analyseSignal(self, backgroundRange=(None,None), signalRange=(None,None), useDetrendedData=True):
        """Analyse the Burst in all tables.

        Args:
            backgroundRange (tuple(float, float)): Time range for background selection, in seconds relative to T0.
            signalRange (tuple(float, float)): Time range for signal selection, in seconds relative to T0.
            useDetrendedData (bool): If True, use detrended data.
        
        Returns:
            results (astropy.table.Table): Results table with Aperture Photometry Information.
        """
        # Set Background and Signal Range from configuration if None
        bkgRange = (backgroundRange[0] if backgroundRange[0] is not None else self.config.getOptionValue("background_tmin"),
                    backgroundRange[1] if backgroundRange[1] is not None else self.config.getOptionValue("background_tmax")
                    )
        sigRange = (signalRange[0] if signalRange[0] is not None else self.config.getOptionValue("signal_tmin"),
                    signalRange[1] if signalRange[1] is not None else self.config.getOptionValue("signal_tmax"))
        
        # Results table
        self.logger.info(f"Analyse Ratemeters Time Series...")
        results = Table(names=("instrument","t_ON","N_ON","t_OFF","N_OFF","R_BKG","lima"),
                        dtype=(str,float,int,float,int,float,float))
        for instr, data_table in self._ratemetersTables.items():
            res = self._analyseTable(data_table, bkgRange, sigRange, useDetrendedData)
            res['instrument'] = instr
            results.add_row(res)
            self.logger.info(f"{instr}: {res['N_ON']} counts above a background rate of {res['R_BKG']} Hz")
        
        # Return
        self.logger.info(f"Done.")
        return results
    
    def estimateDuration(self, dataRange, backgroundRange=(None,None), signalRange=(None,None), useDetrendedData=True, plotDuration=True):
        """Estimate the Duration of the Burst with Cumulative Light Curves.

        Args:
            dataRange (tuple(float, float)): Time range for the plot.
            backgroundRange (tuple(float, float)): Time range for background selection, in seconds relative to T0.
            signalRange (tuple(float, float)): Time range for signal selection, in seconds relative to T0.
            useDetrendedData (bool): If True, use detrended data.
            plotDuration (bool): if True, plot the Cumulative Light Curves.

        Raises:
            ValueError: if dataRange does not contain the Background or Signal Range.

        Returns:
            data_dict (dict): Dictionary of results.
            plot (str or None): Plot output path.
        """
        # Set Background and Signal Range from configuration if None
        bkgRange = (backgroundRange[0] if backgroundRange[0] is not None else self.config.getOptionValue("background_tmin"),
                    backgroundRange[1] if backgroundRange[1] is not None else self.config.getOptionValue("background_tmax")
                    )
        sigRange = (signalRange[0] if signalRange[0] is not None else self.config.getOptionValue("signal_tmin"),
                    signalRange[1] if signalRange[1] is not None else self.config.getOptionValue("signal_tmax"))
        # Data Range Must contain both Signal and Background ranges
        if dataRange[0]>min(bkgRange[0],sigRange[0]): raise ValueError(f"Tmin of Data Range must be <= {min(bkgRange[0],sigRange[0])}")
        if dataRange[1]<max(bkgRange[1],sigRange[1]): raise ValueError(f"Tmax of Data Range must be >= {min(bkgRange[1],sigRange[1])}")
        # Set T0
        T0 = self.config.getOptionValue("T0")
        instruments = ["SA", "MCAL", "AC0"]
        active_instruments = []
        self.logger.info("Computing Duration in SuperAGILE, MCAL and AC Top...")
            
        data_dict={}
        for instr in instruments:
            # Select data in the given data range
            data_full = self._ratemetersTables[instr]
            mask = (data_full['OBT']>T0+dataRange[0])&(data_full['OBT']<T0+dataRange[1])
            time  = data_full[mask]['OBT'].data - T0
            counts= data_full[mask]['COUNTS_D'].data if useDetrendedData else data_full[mask]['COUNTS'].data

            # Subtract Avg background where the detector is active (counts>0)
            bkg_mask = (time>=bkgRange[0])&(time<=bkgRange[1])
            bkg_mean = np.mean(counts[bkg_mask])
            
            # Compute the Cumulative, background subtracted Light Curve where the detector is active
            counts_bkgsub = np.where(counts>0, counts-bkg_mean, 0)
            integral_counts = np.cumsum(counts_bkgsub)

            # Identify the Region where the Signal is rising, within the Signal Window
            sig_mask = (time>=sigRange[0])&(time<=sigRange[1])
            rise_mask= np.diff(integral_counts, prepend=integral_counts[0]) > 0
            sigrise_time = time[sig_mask&rise_mask]
            try:
                duration = sigrise_time[-1] - sigrise_time[0]
            except IndexError:
                duration = 0.0
            
            # Bundle Results for the Plot
            data_dict[instr] = {'time':time,'counts':counts,'counts_bkgsub':counts_bkgsub,'integral_counts':integral_counts,'sigrise_time':sigrise_time,'duration':duration}
            
            # Do not plot if inactive
            if np.max(counts)<1e-3:
                self.logger.warning(f"Detector {instr} not active.")
                continue
            # If active, print results and plot
            self.logger.info(f"Duration (Signal Rise Time) in {instr}: {duration:.3g} s")
            active_instruments.append(instr)
        
        # Plot if requested
        plot = None
        if plotDuration:
            data_flag = "D" if useDetrendedData else "ND"
            filePath = Path(self.outdir).absolute().joinpath(f"plots/ratemeters_duration_{data_flag}.png")
            plot = self.plottingUtils.plotRatemetersDuration(
                data_dict,active_instruments,self.config.getOptionValue("T0"),
                bkgRange, sigRange, dataRange, filePath
                )
        # Return
        self.logger.info(f"Done.")
        return (data_dict, plot)
    
