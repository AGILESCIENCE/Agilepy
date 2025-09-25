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

import numpy as np
import os
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import fits
from astropy.table import Table
from astropy.time import Time
from os.path import join, expandvars
from pathlib import Path

from agilepy.core.AGBaseAnalysis import AGBaseAnalysis
from agilepy.utils.Utils import Utils, expandvars

from agilepy.utils.PlottingUtils import PlottingUtils
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.CustomExceptions import WrongCoordinateSystemError

class AGVisibility(AGBaseAnalysis):
    """This class contains the high-level API methods you can use to run the visibility analysis.

    This class requires you to setup a ``yaml configuration file`` to specify the software's behaviour.

    Class attributes:

    Attributes:
        config (:obj:`AgilepyConfig`): it is used to read/update configuration values.
        logger (:obj:`AgilepyLogger`): it is used to log messages with different importance levels.
    """

    def __init__(self, configurationFilePath):
        """AGVisibility constructor.

        Args:
            configurationFilePath (str): the relative or absolute path to the yaml configuration file.

        Example:
            >>> from agilepy.api import AGVisibility
            >>> ageng = AGVisibility('agconfig.yaml')

        """
        # Load the AGBaseAnalysis object and attributes
        super().__init__(configurationFilePath)
        self.config.loadConfigurationsForClass("AGVisibility")
        self.logger = self.agilepyLogger.getLogger(__name__, "AGVisibility")
        
        # Set attributes
        self._agileTable = None
        self._fermiTable = None
        
        # End initialization
        self.logger.info("AGVisibility initialized")


    @staticmethod
    def getConfiguration(confFilePath, outputDir, logFile,
                         step=30, timeType="tt", tMin="null", tMax="null",
                         fermiSpacecraftFile=None,
                         coord1="null", coord2="null", frame="icrs",
                         userName="my_name", sourceName="vis-source", verboselvl=0
                         ):
        """Utility method to create a configuration file.

        Args:
            confFilePath (str): the path and filename of the configuration file that is going to be created.
            outputDir (str): the path to the output directory. The output directory will be created using the following format: 'userName_sourceName_todaydate'.
            logFile (str): the path to the AGILE logfile containing spacecraft information.
            
            fermiSpacecraftFile (str): the path to the Fermi spacecraft file. Optional.
            step (float): time interval in seconds between 2 consecutive points in the resulting table. Minimum accepted value: 0.1. Default is 30.
            timeType (str): the time format of tMin and tMax.
            tMin, tMax (floa): inferior, superior observation time limit to analize.
            
            coord1, coord2 (float): the coordinates of the source used to compute the offset.
            frame (str): the reference frame of the coordinates.
            
            userName (str): the username of who is running the software.
            sourceName (str): the name of the source.
            verboselvl (int): the verbosity level of the console output. Message types: level 0 => critical, warning, level 1 => critical, warning, info, level 2 => critical, warning, info, debug.

        Returns:
            None
        """

        configuration = f"""

output:
  outdir: \"{outputDir}\"
  filenameprefix: \"visibility_product\"
  sourcename: \"{sourceName}\"
  username: \"{userName}\"
  verboselvl: {verboselvl}

input:
  logfile: \"{logFile}\"
  fermi_spacecraft_file: \"{fermiSpacecraftFile}\"

selection:
  step: {step}
  timetype: \"{timeType}\"
  tmin: {tMin}
  tmax: {tMax}

source:
  coord1: {coord1}
  coord2: {coord2}
  frame: \"{frame}\"

        """
        
        full_file_path = Utils._expandEnvVar(confFilePath)
        parent_directory = Path(full_file_path).absolute().parent
        parent_directory.mkdir(exist_ok=True, parents=True)

        with open(full_file_path,"w") as cf:

            cf.write(configuration)

        return None

    @property
    def agileVisibility(self):
        return self._agileTable
    
    @property
    def fermiVisibility(self):
        return self._fermiTable

    def visibilityPlot(self, logfilesIndex, tmin, tmax, src_x, src_y, ref, zmax=60, step=1, writeFiles=True, computeHistogram=True, saveImage=True, fileFormat="png", title="Visibility Plot"):
        """ Compute the angular separations between the center of the
        AGILE GRID field of view and the coordinates for a given position in the sky,
        given by src_ra and src_dec.

        Args:
            logfilesIndex (str): the index file for the logs files.
            tmin (float): inferior observation time limit to analize.
            tmax (float): superior observation time limit to analize.
            src_x (float): source position x (unit: degrees)
            src_y (float): source position y (unit: degrees)
            zmax (float): maximum zenith distance of the source to the center of the detector (unit: degrees)
            step (integer): time interval in seconds between 2 consecutive points in the resulting plot. Minimum accepted value: 0.1 s.
            writeFiles (bool): if True, two text files with the separions data will be written on file.
            saveImage (bool): If True, the image will be saved on disk
            fileFormat (str): The output format of the image
            title (str): The plot title

        Returns:
            separations (List): the angular separations
            ti_tt (List):
            tf_tt (List):
            ti_mjd (List):
            tf_mjd (List):
            skyCordsFK5.ra.deg
            skyCordsFK5.dec.deg
        """
        logfilesIndex = Utils._expandEnvVar(logfilesIndex)

        separations, ti_tt, tf_tt, ti_mjd, tf_mjd, src_ra, src_dec, sepFile = self._computePointingDistancesFromSource(logfilesIndex, tmin, tmax, src_x, src_y, ref, zmax, step, writeFiles)

        vis_plot = self.plottingUtils.visibilityPlot(separations, ti_tt, tf_tt, ti_mjd, tf_mjd, src_ra, src_dec, zmax, step, saveImage, self.outdir, fileFormat, title)
        hist_plot = None

        if computeHistogram:
            hist_plot = self.plottingUtils.visibilityHisto(separations, ti_tt, tf_tt, src_ra, src_dec, zmax, step, saveImage, self.outdir, fileFormat, title)

        return vis_plot, hist_plot




    def computePointingDirection(self, logfilesIndex=None, tmin=None, tmax=None, timetype=None, step=None, src_x=None, src_y=None, frame=None, writeFiles=True):
        """ Compute the AGILE pointing direction and angular separation from a source in the sky.
        Values which are None are retreived from the configuration file.

        Args:
            logfilesIndex (str): the index file for the logfiles wiith spacecraft information.
            tmin, tmax (float): inferior, superior observation time limit to analize.
            timetype (str): the time format of tmin and tmax.
            step (integer): time interval in seconds between 2 consecutive points the table. Minimum accepted value: 0.1.
            src_x, src_y (float): the coordinates of the source used to compute the offset, in degrees.
            frame (str): the reference frame of the coordinates.
            writeFiles (bool): if True, write the visibility table.

        Returns:
            visibility_tab (astropy.table.Table): the table with the AGILE pointing direction and source separation in degrees.
        """
        # If arguments are not provided explicitly, set them from the configuration
        logfilesIndex = logfilesIndex if logfilesIndex is not None else self.config.getOptionValue("logfile")
        if not os.path.isfile(logfilesIndex):
            raise FileNotFoundError
        
        tmin = tmin if tmin is not None else self.config.getOptionValue("tmin")
        tmax = tmax if tmax is not None else self.config.getOptionValue("tmax")
        timetype = timetype if timetype is not None else self.config.getOptionValue("timetype")
        if timetype != "TT":
            tmin = AstroUtils.convert_time_to_agile_seconds(Time(tmin, format=timetype))
            tmax = AstroUtils.convert_time_to_agile_seconds(Time(tmin, format=timetype))

        step = step if step is not None else self.config.getOptionValue("step")
        if step < 0.1:
            self.logger.critical(f"step {step} cannot be < 0.1")
            raise ValueError(f"\'step\' {step} cannot be < 0.1")
        
        src_x = src_x if src_x is not None else self.config.getOptionValue("coord1")
        src_y = src_y if src_y is not None else self.config.getOptionValue("coord2")
        frame = frame if frame is not None else self.config.getOptionValue("frame")
        
        ##########################################################
        # Get the log files covering the time interval
        logFiles = self._getLogsFileInInterval(logfilesIndex, tmin, tmax)
        self.logger.info(f"Found {len(logFiles)} log files satisfying the interval {tmin}-{tmax}")
        if not logFiles:
            self.logger.warning(f"No log files are compatible with tmin {tmin} and tmax {tmax}")
            return Table()
        total = len(logFiles)

        # Compute the Pointing Direction of AGILE
        self.logger.info(f"Computing AGILE pointing direction. Please wait..")
        all_time_start = []
        all_time_stop = []
        all_agile_ra = []
        all_agile_dec = []
        # Compute logfile by logfile
        for idx, logFile in enumerate(logFiles):
            idx+= 1
            self.logger.info(f"  {idx}/{total} {logFile}")
            doTimeMask = (idx == 1)or(idx == total) # True for first and last file.

            list_time_start, list_time_stop, list_agile_ra, list_agile_dec = self._computePointingPerFile(doTimeMask, logFile, tmin, tmax, step)

            # Append results
            all_time_start.append(list_time_start)
            all_time_stop.append(list_time_stop)
            all_agile_ra.append(list_agile_ra)
            all_agile_dec.append(list_agile_dec)

        # Concatenate results into numpy arrays
        all_time_start = np.concatenate(all_time_start)
        all_time_stop  = np.concatenate(all_time_stop)
        all_agile_ra   = np.concatenate(all_agile_ra)
        all_agile_dec  = np.concatenate(all_agile_dec)
        
        # Convert to Astropy Table
        visibility_tab = Table(
            [all_time_start, all_time_stop, all_agile_ra, all_agile_dec],
            names=('TT_start', 'TT_stop', 'AGILE_RA', 'AGILE_DEC'),
            meta = {}
            )
        visibility_tab['MJD_start'] = AstroUtils.convert_time_from_agile_seconds(visibility_tab['TT_start'].data).mjd
        visibility_tab['MJD_stop' ] = AstroUtils.convert_time_from_agile_seconds(visibility_tab['TT_stop' ].data).mjd

        # Add Source offset column
        try:
            target = SkyCoord(src_x, src_y, frame=frame, unit="deg")
            pointings = SkyCoord(ra=all_agile_ra, dec=all_agile_dec, frame="icrs", unit="deg")
            separations= target.separation(pointings)
            visibility_tab['SOURCE_OFFSET_DEG'] = separations.to("deg").value
            visibility_tab.meta["source_ra_deg"] = target.ra.deg
            visibility_tab.meta["source_dec_deg"]= target.dec.deg
            self.logger.info(f"Computed the source offset from the AGILE pointing direction for a source at RA={src_x}, DEC={src_y}, frame={frame}")
        except Exception as e:
            self.logger.error(f"Cannot compute the pointing-target distance: {e}")
            
        # Set variable
        self._agileTable = visibility_tab
        
        # Write file
        if writeFiles:
            self.logger.info(f"Writing Visibility table in: {self.outdir}")
            output_directory = Path(self.outdir).absolute().joinpath("offaxis_data")
            output_directory.mkdir(exist_ok=True, parents=True)
            filenamePath =  output_directory.joinpath(f"offaxis_distances_{tmin}_{tmax}")
            visibility_tab.write(filenamePath.with_suffix(".csv"), format="csv", overwrite=True)
            self.logger.info(f"Produced: {filenamePath}")

        self.logger.info(f"Done.")
        return visibility_tab

    def _computePointingPerFile(self, doTimeMask, logFile, tmin_start, tmax_start, step):
        """Compute the AGILE pointing direction for a single log file.

        Args:
            logFile (str): path to the logfile with spacecraft data.
            doTimeMask (bool): determine if a time mask must be applied to filter out the data according to the times set in the analysis.
            tmin_start, tmax_start (float): start and stop time for the time mask.
            step (float): filtering step in seconds.

        Returns:
            list_time_start,list_time_stop,list_agile_ra,list_agile_dec (list(float)): lists of the start and stop times and the satellite pointing direction.
        """

        logFile = Utils._expandEnvVar(logFile)
                    
        with fits.open(logFile) as hdulist:
            SC = hdulist[1].data
            self.logger.debug(f"Total events: {len(SC['TIME'])}")
            self.logger.debug(f"tmin: {tmin_start}")
            self.logger.debug(f"tmin log file: {SC['TIME'][0]}")
            self.logger.debug(f"tmax: {tmax_start}")
            self.logger.debug(f"tmax log file: {SC['TIME'][-1]}")
            self.logger.debug(f"Do time mask? {doTimeMask}")

            if doTimeMask:
                self.logger.debug(f"How many times are >= tmin_start? {np.sum(SC['TIME'] >= tmin_start)}")
                self.logger.debug(f"How many times are <= tmax_start? {np.sum(SC['TIME'] <= tmax_start)}")
                # Filtering out
                booleanMask = np.logical_and(SC['TIME'] >= tmin_start, SC['TIME'] <= tmax_start)
                AGILE_TIME = SC['TIME'][booleanMask]
                ATTITUDE_RA_Y = SC['ATTITUDE_RA_Y'][booleanMask]
                ATTITUDE_DEC_Y= SC['ATTITUDE_DEC_Y'][booleanMask]
                self.logger.debug(f"Time mask: {np.sum(np.logical_not(booleanMask))} values skipped")
            else:
                AGILE_TIME = SC['TIME']
                ATTITUDE_RA_Y = SC['ATTITUDE_RA_Y']
                ATTITUDE_DEC_Y= SC['ATTITUDE_DEC_Y']

        # This is to avoid problems with moments for which the AGILE pointing was set to RA=NaN, DEC=NaN
        booleanMaskRA = np.logical_not(np.isnan(ATTITUDE_RA_Y))
        booleanMaskDEC= np.logical_not(np.isnan(ATTITUDE_DEC_Y))
        booleanMaskRADEC = np.logical_or(booleanMaskRA, booleanMaskDEC)
        AGILE_TIME = AGILE_TIME[booleanMaskRA]
        ATTITUDE_RA_Y= ATTITUDE_RA_Y[booleanMaskRADEC]
        ATTITUDE_DEC_Y= ATTITUDE_DEC_Y[booleanMaskRADEC]
        self.logger.debug(f"Not-null mask RA/DEC (at least one NULL): {np.sum(np.logical_not(booleanMaskRADEC))} values skipped")

        deltatime = 0.1 # AGILE attitude is collected every 0.1 s
        index_ti = 0
        index_tf = len(AGILE_TIME)-1
        self.logger.debug(f"Step is: {step}")
        indexstep = int(step*10) # if step 0.1, indexstep=1 => all values
                                 # if step   1, indexstep=10=> one value on 10 values
        self.logger.debug(f"indexstep is: {indexstep}")
        self.logger.debug(f"Number of separations to be computed: {index_tf/indexstep}")

        # Return results
        list_time_start= AGILE_TIME[index_ti:index_tf:indexstep]
        list_time_stop = AGILE_TIME[index_ti:index_tf:indexstep]+deltatime
        list_agile_ra  = ATTITUDE_RA_Y[index_ti:index_tf:indexstep]
        list_agile_dec = ATTITUDE_DEC_Y[index_ti:index_tf:indexstep]
        
        return list_time_start,list_time_stop,list_agile_ra,list_agile_dec



    def _getLogsFileInInterval(self, logfilesIndex, tmin, tmax):
        """Select the log files covering the time interval [tmin, tmax].

        Args:
            logfilesIndex (str): Inex file for the log files.
            tmin, tmax (float): Minimum and maximum time in AGILE seconds (TT).

        Returns:
           logsFiles (list(str)): List of log files covering the time interval [tmin, tmax].
        """

        self.logger.debug( "Selecting files from %s [%d to %d]",logfilesIndex, tmin, tmax)

        logsFiles = []

        with open(logfilesIndex, "r") as lfi:
            lines = [line.strip() for line in lfi.readlines()]

        for line in lines:
            elements = line.split(" ")
            logFilePath = elements[0]
            logFileTmin = float(elements[1])
            logFileTmax = float(elements[2])

            if logFileTmin <= tmax and tmin <= logFileTmax:
                # print(logFileTmin,",",logFileTmax)
                logsFiles.append(logFilePath)

        return logsFiles


