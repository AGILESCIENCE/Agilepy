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
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import fits
from os.path import join, expandvars
from pathlib import Path

from agilepy.core.AGBaseAnalysis import AGBaseAnalysis
from agilepy.utils.Utils import Utils, expandvars

from agilepy.utils.PlottingUtils import PlottingUtils
from agilepy.core.AgilepyLogger import AgilepyLogger
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.CustomExceptions import WrongCoordinateSystemError

class AGEngAgileOffaxisVisibility(AGBaseAnalysis):
    """This class contains the high-level API methods you can use to run engineering analysis.

    This class requires you to setup a ``yaml configuration file`` to specify the software's behaviour.

    Class attributes:

    Attributes:
        config (:obj:`AgilepyConfig`): it is used to read/update configuration values.
        logger (:obj:`AgilepyLogger`): it is used to log messages with different importance levels.
    """

    def __init__(self, configurationFilePath):
        """AGEngAgileOffaxisVisibility constructor.

        Args:
            configurationFilePath (str): the relative or absolute path to the yaml configuration file.

        Example:
            >>> from agilepy.api import AGEngAgileOffaxisVisibility
            >>> ageng = AGEngAgileOffaxisVisibility('agconfig.yaml')

        """
        super().__init__(configurationFilePath)

        self.config.loadConfigurationsForClass("AGEngAgileOffaxisVisibility")
    

    @staticmethod
    def getConfiguration(confFilePath, userName, outputDir, verboselvl):
        """Utility method to create a configuration file.

        Args:
            confFilePath (str): the path and filename of the configuration file that is going to be created.
            userName (str): the username of who is running the software.
            outputDir (str): the path to the output directory. The output directory will be created using the following format: 'userName_sourceName_todaydate'
            verboselvl (int): the verbosity level of the console output. Message types: level 0 => critical, warning, level 1 => critical, warning, info, level 2 => critical, warning, info, debug

        Returns:
            None
        """

        configuration = """
output:
  outdir: %s
  filenameprefix: eng_product
  logfilenameprefix: eng_log
  username: %s
  sourcename: offaxis
  verboselvl: %d

        """%(outputDir, userName, verboselvl)

        with open(Utils._expandEnvVar(confFilePath),"w") as cf:

            cf.write(configuration)



    def visibilityPlot(self, logfilesIndex, tmin, tmax, src_x, src_y, ref, zmax=60, step=1, writeFiles=True, computeHistogram=True, saveImage=True, fileFormat="png", title="Visibility Plot"):
        """ It computes the angular separations between the center of the
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

    def _computePointingDistancesFromSource(self, logfilesIndex, tmin, tmax, src_x, src_y, ref, zmax, step, writeFiles):
        """ It computes the angular separations between the center of the
        AGILE GRID field of view and the coordinates for a given position in the sky,
        given by src_ra and src_dec.

        Args:
            tmin (float): inferior observation time limit to analize.
            tmax (float): superior observation time limit to analize.
            src_x (float): source position x (unit: degrees)
            src_y (float): source position y (unit: degrees)
            zmax (float): maximum zenith distance of the source to the center of the detector (unit: degrees)
            step (integer): time interval in seconds between 2 consecutive points in the resulting plot. Minimum accepted value: 0.1 s.
            writeFiles (bool): if True, two text files with the separions data will be written on file.
            logfilesIndex (str) (optional): the index file for the logs files. If specified it will ovverride the one in the configuration file.


        Returns:
            separations (List): the angular separations
            ti_tt (List):
            tf_tt (List):
            ti_mjd (List):
            tf_mjd (List):
            skyCordsFK5.ra.deg
            skyCordsFK5.dec.deg
        """
        self.logger.info(self, "Computing pointing distances from source (%f, %f) %s in [%f, %f]",src_x, src_y, ref, tmin, tmax)

        if not logfilesIndex:
            raise ValueError("'logfilesIndex' cannot be None")

        if ref == "equ":
            skyCordsFK5 = SkyCoord(ra=src_x*u.degree, dec=src_y*u.degree, frame='fk5')

        elif ref == "gal":
            skyCordsGAL = SkyCoord(l=src_x*u.degree, b=src_y*u.degree, frame='galactic')
            #skyCordsICRS = skyCordsGAL.transform_to('icrs')
            skyCordsFK5 = skyCordsGAL.transform_to('fk5')

        else:
            self.logger.critical(self, "Reference system '%s' is not supported", ref)
            raise WrongCoordinateSystemError("Reference system '%s' is not supported" %(ref))

        if step < 0.1:
            self.logger.critical(self, "step %f cannot be < 0.1", step)
            raise ValueError("'step' %f cannot be < 0.1"%(step))

        self.logger.debug(self, "Galactict coords: l:%f b:%f", skyCordsGAL.l.deg,skyCordsGAL.b.deg)

        self.logger.debug(self, "FK5 coords: ra:%f dec:%f ", skyCordsFK5.ra.deg,skyCordsFK5.dec.deg)

        logFiles = self._getLogsFileInInterval(logfilesIndex, tmin, tmax)

        self.logger.info(self, "%d log files satisfy the interval %f-%f", len(logFiles), tmin, tmax)

        if not logFiles:
            self.logger.warning(self, "No log files can are compatible with tmin %f and tmax %f", tmin, tmax)
            return [], [], [], [], [], skyCordsFK5.ra.deg, skyCordsFK5.dec.deg, None


        total = len(logFiles)
        tmin_start = tmin
        tmax_start = tmax

        separation_tot = None
        ti_tt_tot = None
        tf_tt_tot = None
        init = False

        self.logger.info(self, "Computing pointing distances. Please wait..")

        for idx, logFile in enumerate(logFiles):

            idx = idx + 1

            self.logger.info(self, "%d/%d %s", idx, total, logFile)

            if idx == 1 or idx == total:
                doTimeMask = True
            else:
                doTimeMask = False


            separation, ti_tt, tf_tt = self._computeSeparationPerFile(doTimeMask, logFile, tmin_start, tmax_start, skyCordsFK5, zmax, step)

            if not init:
                separation_tot = separation
                ti_tt_tot = ti_tt
                tf_tt_tot = tf_tt
                init = True
            else:
                separation_tot = np.concatenate((separation_tot, separation), axis=0)
                ti_tt_tot = np.concatenate((ti_tt_tot, ti_tt), axis=0)
                tf_tt_tot = np.concatenate((tf_tt_tot, tf_tt), axis=0)

            self.logger.debug(self, "Total computed separations: %d", len(separation_tot))

        # Conversion TT => MJD
        self.logger.info(self, "Converting ti_tt_tot from TT to MJD..Number of elements=%d", len(ti_tt_tot))
        ti_mjd = AstroUtils.time_mjd_to_agile_seconds(ti_tt_tot)

        self.logger.info(self, "Converting tf_tt_tot from TT to MJD..Number of elements=%d", len(tf_tt_tot))
        tf_mjd = AstroUtils.time_mjd_to_agile_seconds(tf_tt_tot)

        """
        self.logger.info(self, "Computig meantimes..Number of elements=%d", len(ti_mjd))
        meantimes = (ti_mjd+tf_mjd)/2.

        if writeFiles:
            zmax = zmax*u.deg
            ttotal_under_zmax = np.sum(tf_tt_tot[separation_tot<zmax]-ti_tt_tot[separation_tot<zmax])
            ttotal_above_zmax = np.sum(tf_tt_tot[separation_tot>zmax]-ti_tt_tot[separation_tot>zmax])
            kk = open(join(self.outdir,"times_bins_vs_separation.txt"), "w")
            filesep = open(join(self.outdir,'time_vs_separation_agile.txt'), 'w')
            for i in np.arange(len(separation_tot)):
                filesep.write("{} {}\n".format(meantimes[i], separation_tot[i]))
                kk.write("{} {} {}\n".format(ti_tt_tot[i], tf_tt_tot[i], separation_tot[i]))
            filesep.close()
            kk.close()
        """


        self.logger.debug(self, "separation_tot len: %d", len(separation_tot))
        self.logger.debug(self, "ti_tt_tot len: %d", len(ti_tt_tot))
        self.logger.debug(self, "tf_tt_tot len: %d", len(tf_tt_tot))

        filenamePath = None
        if writeFiles:

            filename = f"offaxis_distances_{tmin}_{tmax}"
            outdirPath = Path(self.outdir).joinpath("offaxis_data")
            outdirPath.mkdir(parents=True, exist_ok=True)
            filenamePath = outdirPath.joinpath(filename)
            np.save(filenamePath, separation_tot, allow_pickle=True)
            self.logger.info(self, "Produced: %s", filenamePath)


        return separation_tot, ti_tt_tot, tf_tt_tot, ti_mjd, tf_mjd, skyCordsFK5.ra.deg, skyCordsFK5.dec.deg, filenamePath

    def _computeSeparationPerFile(self, doTimeMask, logFile, tmin_start, tmax_start, skyCordsFK5, zmax, step):

        logFile = Utils._expandEnvVar(logFile)
                    
        hdulist = fits.open(logFile)
        SC = hdulist[1].data
        self.logger.debug(self, "Total events: %f", len(SC["TIME"]))
        self.logger.debug(self,"tmin: %f",tmin_start)
        self.logger.debug(self,"tmin log file: %f",SC["TIME"][0])
        self.logger.debug(self,"tmax: %f",tmax_start)
        self.logger.debug(self,"tmax log file: %f",SC["TIME"][-1])

        self.logger.debug(self, "Do time mask? %d",doTimeMask)

        if doTimeMask:

            self.logger.debug(self, "How many times are >= tmin_start? %d",np.sum(SC['TIME'] >= tmin_start))
            self.logger.debug(self, "How many times are <= tmax_start? %d",np.sum(SC['TIME'] <= tmax_start))

            # Filtering out
            booleanMask = np.logical_and(SC['TIME'] >= tmin_start, SC['TIME'] <= tmax_start)
            TIME = SC['TIME'][booleanMask]
            ATTITUDE_RA_Y= SC['ATTITUDE_RA_Y'][booleanMask]
            ATTITUDE_DEC_Y= SC['ATTITUDE_DEC_Y'][booleanMask]
            self.logger.debug(self, "Time mask: %d values skipped"%(np.sum(np.logical_not(booleanMask))))


        else:
            TIME = SC['TIME']
            ATTITUDE_RA_Y= SC['ATTITUDE_RA_Y']
            ATTITUDE_DEC_Y= SC['ATTITUDE_DEC_Y']

        hdulist.close()

        # This is to avoid problems with moments for which the AGILE pointing was set to RA=NaN, DEC=NaN
        booleanMaskRA = np.logical_not(np.isnan(ATTITUDE_RA_Y))
        booleanMaskDEC = np.logical_not(np.isnan(ATTITUDE_DEC_Y))

        booleanMaskRADEC = np.logical_or(booleanMaskRA, booleanMaskDEC)

        TIME = TIME[booleanMaskRA]
        ATTITUDE_RA_Y= ATTITUDE_RA_Y[booleanMaskRADEC]
        ATTITUDE_DEC_Y= ATTITUDE_DEC_Y[booleanMaskRADEC]

        self.logger.debug(self, "Not-null mask RA/DEC (at least one NULL): %d values skipped"%(np.sum(np.logical_not(booleanMaskRADEC))))


        deltatime = 0.1 # AGILE attitude is collected every 0.1 s

        # tmin = np.min(TIME)
        # tmax = np.max(TIME)

        index_ti = 0
        index_tf = len(TIME)-1

        self.logger.debug(self, "Step is: %f",step)

        indexstep = int(step*10) # if step 0.1 , indexstep=1 => all values
                            # if step 1 , indexstep=10 => one value on 10 values

        self.logger.debug(self, "indexstep is: %f",indexstep)

        # creating arrays filled with zeros
        src_raz  = np.zeros(len(TIME[index_ti:index_tf:indexstep]))
        src_decz  = np.zeros(len(TIME[index_ti:index_tf:indexstep]))

        self.logger.debug(self, "Number of separations to be computed: %f", index_tf/indexstep)

        # filling the just created arrays with our coordinates of interest
        src_ra   = src_raz + skyCordsFK5.ra
        src_dec   = src_decz + skyCordsFK5.dec

        c1  = SkyCoord(src_ra, src_dec, unit='deg', frame='icrs')
        c2  = SkyCoord(ATTITUDE_RA_Y[index_ti:index_tf:indexstep], ATTITUDE_DEC_Y[index_ti:index_tf:indexstep], unit='deg', frame='icrs')
#        print 'c1=', len(c1), 'c2=', len(c2) # to ensure c1 and c2 have the same length
        sep = c2.separation(c1)

        self.logger.debug(self, "Number of computed separation: %f"%(len(sep)))

        return np.asfarray(sep), TIME[index_ti:index_tf:indexstep], TIME[index_ti:index_tf:indexstep]+deltatime

    def _getLogsFileInInterval(self, logfilesIndex, tmin, tmax):

        self.logger.debug(self, "Selecting files from %s [%d to %d]",logfilesIndex, tmin, tmax)

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





    # from agilepy.utils.PlottingUtils import PlottingUtils
    # pu = PlottingUtils()
    # pu.visibilityPlot(sep, time_s, tf_tt, ra, dec, zmax, step, twocolumn=False, histogram=True, im_fmt='png', plot=True, outDir="./images")
    # pu.visibilityHistogram(sep, )
