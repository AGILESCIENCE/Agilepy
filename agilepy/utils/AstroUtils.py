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

                return math.sqrt(d1 * d1 + d2 * d2)
    
    @staticmethod
    def evaluate_erglog_from_flux(E, flux, E1, E2, alpha):
        """
        Evaluate SED erglog at energy E assuming power law with index alpha. Energies E, E1, E2 are in MeV.

        Args:
            E
        Returns:

        """

    @staticmethod
    def evaluate_erglog_from_flux(flux, E1, E2, alpha):
        """
        Given a flux, computed between E1 (MeV) and E2 (MeV) assuming power law with index alpha,
        Evaluate SED erglog at energy log center between E1 and E2.

        Args:
            flux: in ph/cm2/s
            E1: in MeV
            E2: in MeV
            alpha: power law index

        Returns:
            SED erglog at energy log center between E1 and E2
        """
        # MeV to erg
        factor=0.00000160217733
        # Ecsquared factor
        Ecsquared=E1*E2
        # Reference Energy where evaluate SED
        log10_E = ( np.log10(E1) + np.log10(E2) ) /2.0
        E = np.power(10, log10_E)
        # Evaluate and return SED
        return flux*np.power(factor, 3-alpha)*np.power(E,2-alpha)*Ecsquared/(E2-E1)

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
    # AGILE_DELTA: 2004-01-01 00:00:00.000 # MJD 53005
    
    UNIX_FERMI_DELTA = 978307200
    # FERMI_DELTA: 2001-01-01 00:00:00.000 # MJD 51910
    
    ############################
    # Generic Conversion functions
    @staticmethod
    def convert_time_to_agile_seconds(t):
        """Convert an astropy time object to AGILE seconds.

        Args:
            t (astropy.time.Time): Time Object.

        Returns:
            agile_time (float): Time in AGILE TT format.
        """
        agile_time = t.unix - AstroUtils.UNIX_AGILE_DELTA
        return agile_time
    
    @staticmethod
    def convert_time_from_agile_seconds(time_agile_seconds):
        """Convert time from AGILE seconds format to an astropy time object.

        Args:
            time_agile_seconds (float): Time in AGILE TT format.

        Returns:
            t (astropy.time.Time): Time Object.
        """
        time_unix = np.array(time_agile_seconds) + AstroUtils.UNIX_AGILE_DELTA
        t = Time(time_unix, format="unix")
        return t
    
    @staticmethod
    def convert_time_to_fermi_seconds(t):
        """Convert an astropy time object to FERMI seconds.

        Args:
            t (astropy.time.Time): Time Object.

        Returns:
            fermi_time (float): Time in Fermi MET format.
        """
        fermi_time = t.unix - AstroUtils.UNIX_FERMI_DELTA
        return fermi_time
    
    @staticmethod
    def convert_time_from_fermi_seconds(time_fermi_seconds):
        """Convert time from Fermi seconds format to an astropy time object.

        Args:
            time_fermi_seconds (float): Time in Fermi MET format.

        Returns:
            t (astropy.time.Time): Time Object.
        """
        time_unix = np.array(time_fermi_seconds) + AstroUtils.UNIX_FERMI_DELTA
        t = Time(time_unix, format="unix")
        return t
    
    @staticmethod
    def time_fermi_to_agile(fermi_time):
        """Convert Fermi MET (s since 2001-01-01) to AGILE time (s since 2004-01-01).
        
        Args:
            fermi_time (float): Time in Fermi MET format.
            
        Returns:
            agile_time (float): Time in AGILE TT format.
        """
        AGILE_OFFSET_FROM_FERMI = AstroUtils.UNIX_AGILE_DELTA - AstroUtils.UNIX_FERMI_DELTA
        agile_time = fermi_time - AGILE_OFFSET_FROM_FERMI
        return agile_time

    @staticmethod
    def time_agile_to_fermi(agile_time):
        """Convert AGILE time (s since 2004-01-01) to Fermi MET (s since 2001-01-01).
        
        Args:
            agile_time (float): Time in AGILE TT format.
            
        Returns:
            fermi_time (float): Time in Fermi MET format.
        """
        AGILE_OFFSET_FROM_FERMI = AstroUtils.UNIX_AGILE_DELTA - AstroUtils.UNIX_FERMI_DELTA
        fermi_time = agile_time + AGILE_OFFSET_FROM_FERMI
        return fermi_time
    
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
        time_unix = np.array(time_agile_seconds) + AstroUtils.UNIX_AGILE_DELTA
        return np.round(time_unix)

    @staticmethod
    def time_agile_seconds_to_mjd(time_agile_seconds):
        time_unix = np.array(time_agile_seconds) + AstroUtils.UNIX_AGILE_DELTA
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
    
    ###############
    @staticmethod
    def li_ma(n_on:int, n_off:int, alpha:float):
        """Compute Li&Ma Significance if enough counts are provided.

        Args:
            n_on (int): ON counts.
            n_off (int): OFF counts.
            alpha (float): Exposure Ratio ON / OFF region.

        Returns:
            significance (float): Li&Ma Significance
        """

        if n_on < 10 or n_off < 10 or alpha == 0:
            return 0.0
        fc = (1 + alpha) / alpha
        fb = n_on / (n_on + n_off)
        f  = fc * fb
        
        gc = 1 + alpha
        gb = n_off / (n_on + n_off)
        g  = gc * gb
        
        first  = n_on * np.log(f)
        second = n_off * np.log(g)
        
        fullb   = first + second
        significance = np.sqrt(2) * np.sqrt(fullb)
        
        return significance
