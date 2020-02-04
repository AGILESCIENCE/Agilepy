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

class AGEng:

    @staticmethod
    def computeAGILEAngularDistanceFromSource(logfilesIndex, tmin, tmax, l=None, b=None, ra=None, dec=None, zmax=60):

        if l is not None and b is not None:
            skyCords = SkyCoord(l=l*u.degree, b=b*u.degree, frame='galactic')
        else:
            skyCords = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')

        logFiles = AGEng._getLogsFileInInterval(logfilesIndex, tmin, tmax)
        print(logFiles)

        if not logFiles:
            print("No files.")
            exit(1)

        data = AGEng._calcSeparation(logFiles, tmin, tmax, skyCordsFK5, zmax)
        print(data)



    @ staticmethod
    def _calcSeparation(logFiles, tmin, tmax, skyCordsFK5, zmax):
        """ Function that computes the angular separation between the center of the
        AGILE GRID field of view and the coordinates for a given position in the sky,
        given by src_ra and src_dec.

        - logfilesIndex:
        - src_ra: float, right ascension of the source of interest (unit: degrees)
        - src_dec: float, declination of the source of interest (unit: degrees)
        - zmax: maximum zenith distance of the source to the center of the detector
          (unit: degrees)
        - tmin(optional): float, inferior observation time limit to analize.
          If left blank, timelimiti is set to the initial time in the agile_spacecraft
          file
        - tmax (optional): float, inferior observation time limit to analize.
          If left blank, timelimiti is set to the final time in the agile_spacecraft
          file
        - step (optional): integer, time interval in seconds between 2 consecutive points
          in the resulting plot. Minimum accepted value: 0.1 s. If left blank, step=0.1 is
          chosen

          Output: separation (array), time_i (array), time_f (array)

        """

        for idx, logFile in enumerate(logFiles):

            hdulist = fits.open(logFile)

            SC = hdulist[1].data

            if idx == 0 or idx == len(logFiles)-1:
                # Filtering out
                booleanMask = SC['TIME'] >= tmin and SC['TIME'] <= tmax
                TIME = SC['TIME'][booleanMask]
                ATTITUDE_RA_Y= SC['ATTITUDE_RA_Y'][booleanMask]
                ATTITUDE_DEC_Y= SC['ATTITUDE_DEC_Y'][booleanMask]
            else:
                TIME = SC['TIME']
                ATTITUDE_RA_Y= SC['ATTITUDE_RA_Y']
                ATTITUDE_DEC_Y= SC['ATTITUDE_DEC_Y']


            # This is to avoid problems with moments for which the AGILE pointing was set to RA=NaN, DEC=NaN
            booleanMaskRA = np.logical_not(np.isnan(SC['ATTITUDE_RA_Y']))
            booleanMaskDEC = np.logical_not(np.isnan(SC['ATTITUDE_RA_Y']))
            TIME = TIME[booleanMaskRA]
            ATTITUDE_RA_Y= ATTITUDE_RA_Y[booleanMaskRA]
            ATTITUDE_DEC_Y= ATTITUDE_DEC_Y[booleanMaskDEC]


            deltatime = 0.1 # AGILE attitude is collected every 0.1 s

            # if non specified, the initial and final time will be the first and last time in the SC file, respectively
            if tmin < np.min(TIME):
                tmin = np.min(TIME)
            if tmax > np.max(TIME):
                tmax = np.max(TIME)

            index_ti = 0
            index_tf = len(TIME)-1

            # creating arrays filled with zeros
            src_raz  = np.zeros(len(TIME[index_ti:index_tf:int(step)]))
            src_decz  = np.zeros(len(TIME[index_ti:index_tf:int(step)]))

            # filling the just created arrays with our coordinates of interest
            src_ra   = src_raz + skyCordsFK5.ra
            src_dec   = src_decz + skyCordsFK5.dec

            c1  = SkyCoord(src_ra, src_dec, unit='deg', frame='icrs')
            c2  = SkyCoord(ATTITUDE_RA_Y[index_ti:index_tf:int(step)], ATTITUDE_DEC_Y[index_ti:index_tf:int(step)], unit='deg', frame='icrs')
    #        print 'c1=', len(c1), 'c2=', len(c2) # to ensure c1 and c2 have the same length
            sep = c2.separation(c1)

        return np.asfarray(sep), TIME[index_ti:index_tf:int(step)], TIME[index_ti:index_tf:int(step)]+deltatime

    @staticmethod
    def _getLogsFileInInterval(logfilesIndex, tmin, tmax):

        logsFiles = []

        with open(logfilesIndex, "r") as lfi:
            lines = [line.strip() for line in lfi.readlines()]

        for line in lines:
            elements = line.split(" ")
            logFilePath = elements[0]
            logFileTmin = float(elements[1])
            logFileTmax = float(elements[2])

            if logFileTmin <= tmax and tmin <= logFileTmax:

                logsFiles.append(AgilepyConfig._expandEnvVar(logFilePath))

        return logsFiles


if __name__ == "__main__":

    file = "/opt/anaconda3/envs/agilepy/agiletools/agilepy-test-data/log_index/agile_proc3_data_asdc2_LOG.log.index"

    AGEng.computeAGILEAngularDistanceFromSource(file, 221572734, 228830334, l=129.7, b=3.7, zmax=60)
