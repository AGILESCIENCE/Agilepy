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

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import math
import numpy as np
import pandas as pd
from datetime import datetime
from astropy.time import Time

class AstroUtils:

    @staticmethod
    def distance(l1, b1, l2, b2):
        """
        Computes the angular distance between two galatic coordinates.

        Args:
            l1 (float): longitude of first coordinate
            b1 (float): latitude of first coordinate
            l2 (float): longitude of second coordinate
            b2 (float): latitude of second coordinate

        Returns:
            the angular distance between (l1, b1) and (l2, b2)
        """
        if l1 < 0 or l1 > 360 or l2 < 0 or l2 > 360:
            return -2
        elif b1 < -90 or b1 > 90 or b2 < -90 or b2 > 90:
            return -2
        else:
            d1 = b1 - b2
            d2 = l1 - l2

            b11 = math.pi / 2.0 - (b1 * math.pi / 180.0)
            b21 = math.pi / 2.0 - (b2 * math.pi / 180.0)
            m4 = math.cos(b11) * math.cos(b21) + math.sin(b11) * math.sin(b21) * math.cos(d2 * math.pi / 180.0)
            if m4 > 1:
                m4 = 1

            try:
                return math.acos(m4) * 180.0 / math.pi

            except Exception as e:

                print("\nException in AstroUtils.distance (error in acos() ): ", e)

                return math.sqrt(d1 * d1 + d2 * d2)
    
    @staticmethod
    def AP_filter(filename, threshold, tstart, tstop, outpath):
        """
        This function filters an aperture photometry file using a threshold value for exposure,
        it discards the rows lower than threshold and returns a new file merging the continous rows.

        Args:
            filename (str): path of the aperture photometry file
            threshold (float): exposure threshold
            tstart (float): time start in UTC
            tstop (float): time stop in UTC
        
        Returns:
            A filtered file result.txt
        """

        data = pd.read_csv(filename,  index_col=False, names=["tmin_tt", "tmax_tt", "exp", "cts"], sep=" ")

        data = data[data["exp"] > threshold]
        data.sort_values("tmin_tt", inplace=True)
        data["group"] = (data["tmin_tt"] > data["tmax_tt"].shift()).cumsum()
        results = data.groupby("group").agg({"tmin_tt":"min", "tmax_tt":"max"})
        results.to_csv(str(outpath)+"/result.txt", sep=" ", index=False)

        data = pd.read_csv(str(outpath)+"/result.txt", sep=" ", header=0)

        data = data[data["tmin_tt"] > tstart]
        data = data[data["tmax_tt"] < tstop]

        product = str(outpath)+"/result"+"_"+str(tstart) + "_" + str(tstop)+".txt"
        data.to_csv(product, sep=" ", index=False)

        print(product)

        return product



    ############################################################################
    #
    #   Astropy implementation
    #  
    #   https://docs.astropy.org/en/stable/time/index.html
    #
    #   The time "format" specifies how an instant of time is represented.
    #   https://docs.astropy.org/en/stable/time/index.html#time-format
    #
    #   The time "scale" (or time standard) is 'a specification for measuring time: 
    #   either the rate at which time passes; or points in time; or both'
    #   https://docs.astropy.org/en/stable/time/index.html#time-scale
    #
    #   UNIX_AGILE_DELTA = 1072915200
    #   AGILE_TIME = UNIX_TIME - UNIX_AGILE_DELTA
    #
    #   Supported formats = ["jd", "mjd", "fits", "iso", "unix", "agile seconds since 2004"]
    
    UNIX_AGILE_DELTA = 1072915200
    
    ############################
    # Input: JD

    @staticmethod
    def time_jd_to_mjd(time_jd):
        t = Time(time_jd, format="jd")
        return t.mjd

    @staticmethod
    def time_jd_to_fits(time_jd):
        t = Time(time_jd, format="jd")
        return t.fits

    @staticmethod
    def time_jd_to_iso(time_jd):
        t = Time(time_jd, format="jd")
        return t.iso       

    @staticmethod
    def time_jd_to_unix(time_jd):
        t = Time(time_jd, format="jd")
        return np.round(t.unix)        
        
    @staticmethod
    def time_jd_to_agile_seconds(time_jd):
        t = Time(time_jd, format="jd")
        return np.round(t.unix - AstroUtils.UNIX_AGILE_DELTA)
    
    
    ############################
    # Input: AGILE SECONDS

    @staticmethod
    def time_agile_seconds_to_jd(time_agile_seconds):
        time_unix = time_agile_seconds + AstroUtils.UNIX_AGILE_DELTA
        t = Time(time_unix, format="unix")
        return t.jd

    @staticmethod
    def time_agile_seconds_to_fits(time_agile_seconds):
        time_unix = time_agile_seconds + AstroUtils.UNIX_AGILE_DELTA
        t = Time(time_unix, format="unix")
        return t.fits

    @staticmethod
    def time_agile_seconds_to_iso(time_agile_seconds):
        time_unix = time_agile_seconds + AstroUtils.UNIX_AGILE_DELTA
        t = Time(time_unix, format="unix")
        return t.iso
    
    @staticmethod
    def time_agile_seconds_to_unix(time_agile_seconds):
        time_unix = time_agile_seconds + AstroUtils.UNIX_AGILE_DELTA
        return np.round(time_unix)

    @staticmethod
    def time_agile_seconds_to_mjd(time_agile_seconds):
        time_unix = time_agile_seconds + AstroUtils.UNIX_AGILE_DELTA
        t = Time(time_unix, format="unix")
        return t.mjd

    ############################
    # Input: MJD

    @staticmethod
    def time_mjd_to_jd(time_mjd):
        t = Time(time_mjd, format="mjd")
        return t.jd

    @staticmethod
    def time_mjd_to_fits(time_mjd):
        t = Time(time_mjd, format="mjd")
        return t.fits

    @staticmethod
    def time_mjd_to_iso(time_mjd):
        t = Time(time_mjd, format="mjd")
        return t.iso
    
    @staticmethod
    def time_mjd_to_unix(time_mjd):
        t = Time(time_mjd, format="mjd")
        return np.round(t.unix)

    @staticmethod
    def time_mjd_to_agile_seconds(time_mjd):
        t = Time(time_mjd, format="mjd")
        return np.round(t.unix - AstroUtils.UNIX_AGILE_DELTA)

    ############################
    # Input: ISO

    @staticmethod
    def time_iso_to_jd(time_iso):
        t = Time(time_iso, format="iso")
        return t.jd

    @staticmethod
    def time_iso_to_fits(time_iso):
        t = Time(time_iso, format="iso")
        return t.fits

    @staticmethod
    def time_iso_to_unix(time_iso):
        t = Time(time_iso, format="iso")
        return np.round(t.unix)

    @staticmethod
    def time_iso_to_agile_seconds(time_iso):
        t = Time(time_iso, format="iso")
        return np.round(t.unix - AstroUtils.UNIX_AGILE_DELTA)

    @staticmethod
    def time_iso_to_mjd(time_iso):
        t = Time(time_iso, format="iso")
        return t.mjd
        
    ############################
    # Input: FITS

    @staticmethod
    def time_fits_to_jd(time_fits):
        t = Time(time_fits, format="fits")
        return t.jd

    @staticmethod
    def time_fits_to_mjd(time_fits):
        t = Time(time_fits, format="fits")
        return t.mjd

    @staticmethod
    def time_fits_to_iso(time_fits):
        t = Time(time_fits, format="fits")
        return t.iso

    @staticmethod
    def time_fits_to_unix(time_fits):
        t = Time(time_fits, format="fits")
        return np.round(t.unix)

    @staticmethod
    def time_fits_to_agile_seconds(time_fits):
        t = Time(time_fits, format="fits")
        return np.round(t.unix - AstroUtils.UNIX_AGILE_DELTA)

            
    ############################
    # Input: UNIX
    
    @staticmethod
    def time_unix_to_jd(time_unix):
        t = Time(time_unix, format="unix")
        return t.jd

    @staticmethod
    def time_unix_to_mjd(time_unix):
        t = Time(time_unix, format="unix")
        return t.mjd

    @staticmethod
    def time_unix_to_fits(time_unix):
        t = Time(time_unix, format="unix")
        return t.fits

    @staticmethod
    def time_unix_to_iso(time_unix):
        t = Time(time_unix, format="unix")
        return t.iso

    @staticmethod
    def time_unix_to_agile_seconds(time_unix):
        t = Time(time_unix, format="unix")
        return np.round(t.unix - AstroUtils.UNIX_AGILE_DELTA)