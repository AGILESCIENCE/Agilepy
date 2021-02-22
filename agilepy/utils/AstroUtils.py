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
    def filter(filename, threshold, tstart, tstop, outpath):
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




    # BASIC CONVERSIONS
    @staticmethod
    def time_mjd_to_tt(timemjd):
        """
        Convert mjd to tt. Tolerance = 0.001 s

        Args:
            timemjd (float): time in mjd format

        Returns:
            the input converted in tt format.
        """
        return (timemjd - 53005.0) * 86400.0

    @staticmethod
    def time_tt_to_mjd(timett):
        """
        Convert tt to mjd. Tolerance = 0.0000001 s

        Args:
            timett (float): time in tt format

        Returns:
            the input converted in mjd format.
        """
        return (timett / 86400.0) + 53005.0

    @staticmethod
    def time_nparray_mjd_to_tt(timemjd_nparray):
        if not isinstance(timemjd_nparray, np.ndarray):
            timemjd_nparray = np.array(timemjd_nparray)
        return (timemjd_nparray - 53005.0) * 86400.0

    @staticmethod
    def time_nparray_tt_to_mjd(timett_nparray):
        if not isinstance(timett_nparray, np.ndarray):
            timett_nparray = np.array(timett_nparray)
        return (timett_nparray / 86400.0) + 53005.0

    @staticmethod
    def time_tt_to_utc(timett) -> str:
        """
        Convert tt to utc. Tolerance = 1 s

        Args:
            timett (float): time in tt format

        Returns:
            input converted in utc format (string).
        """
        utc_offset = 2400000.5
        mjdref = 53005.0
        sod = 86400.0
        sec_offset = 43200.0

        a = AstroUtils.jd_to_civil(utc_offset + mjdref + ( (timett + sec_offset)/sod ))
        #print("jd_to_civil:",a)
        b = AstroUtils.day_fraction_to_time(a[2] % 1)
        #print("day_fraction_to_time:",b)
        # utc = [a[0] , a[1] , float(int(a[2])), b[0] , b[1] , b[2] , b[3]]
        utc_s = "%s-%02d-%02dT%02d:%02d:%02d"%(str(a[0]), int(a[1]), int(a[2]), b[0], b[1], b[2])
        return utc_s

    @staticmethod
    def to_jd(dt, fmt = 'jd'):
        """
        Converts a given datetime object to Julian date (jd o mjd). Tolerance = 0.00000001 days

        Args:
            dt (datetime): time in datetime format
            fmt (str): jd or mjd

        Returns:
            input converted in jd format (jd o mjd).
        """
        a = math.floor((14-dt.month)/12)
        y = dt.year + 4800 - a
        m = dt.month + 12*a - 3

        jdn = dt.day + math.floor((153*m + 2)/5) + 365*y + math.floor(y/4) - math.floor(y/100) + math.floor(y/400) - 32045

        jd = jdn + (dt.hour - 12) / 24 + dt.minute / 1440 + dt.second / 86400 + dt.microsecond / 86400000000

        if fmt.lower() == 'jd':
            return jd
        elif fmt.lower() == 'mjd':
            return jd - 2400000.5
        else: # fmt.lower() == 'rjd':
            return jd - 2400000

    @staticmethod
    def time_utc_to_tt(timeutc):
        """
        Convert utc to tt. Tolerance = 0.0001 s

        Args:
            timeutc (str): time in utc format

        Returns:
            input converted in tt format.
        """
        #ls1 = timeutc.split("T")[0]
        ls2 = timeutc.split("T")[1]
        #year=ls1.split("-")[0]
        #month=ls1.split("-")[1]
        #day=ls1.split("-")[2]
        hour=ls2.split(":")[0]
        min=ls2.split(":")[1]
        sec=ls2.split(":")[2]

        utc_offset = 2400000.5
        mjdref = 53005.0
        sod = 86400.0
        sec_offset = 43200.0
        fod = AstroUtils.time_to_day_fraction( int(hour) , int(min) , int(sec) )
        #print("fod:\n",fod)

        dt = datetime.strptime(timeutc, '%Y-%m-%dT%H:%M:%S')

        jd = int(round(AstroUtils.to_jd(dt, fmt='jd')))
        #print("jd:\n",jd)

        jd = jd + fod
        #print("jd+fod:\n",jd)

        tt = (jd - utc_offset - mjdref) * sod
        #print("utc_offset:\n",utc_offset)
        #print("mjdref:\n",mjdref)
        #print("sod:\n",sod)
        #print("tt:\n",tt)

        tt -= sec_offset
        #print("sec_offset:\n",sec_offset)
        #print("tt-sec_offset:\n",tt)

        return tt

    @staticmethod
    def day_fraction_to_time(fr):
        """
        Convert a fractional day to [hours, minutes, seconds, fraction_of_a_second]
        Args:
            fr (float): fractional day

        Returns:
            input converted to [hours, minutes, seconds, fraction_of_a_second] (List).
        """
        ss,  fr = divmod(fr, 1/86400)
        h,   ss = divmod(ss, 3600)
        min, s  = divmod(ss, 60)
        return h, min, s, fr

    @staticmethod
    def time_to_day_fraction(h, min, s):
        """
        Convert hours,minutes and seconds to a fraction of day.

        Args:
            timeutc (float): time in utc format
            timeutc (float): time in utc format
            timeutc (float): time in utc format

        Returns:
            input converted in a fraction of day.
        """
        return (h * 3600 + min * 60 + s)/86400

    @staticmethod
    def jd_to_civil(jd):
        """
        Convert a Julian Day Number to a Civil Date. Tolerance = 0.043 days

        Args:
            jd (float): the Julian Day Number.

        Returns:
            Returns the corresponding [year, month, day_of_month] as a List.
        """
        x = math.floor((jd - 1867216.25) / 36524.25)
        a = jd + 1 + x - math.floor(x / 4.0)

        b = a + 1524
        c = math.floor((b - 122.1) / 365.25)
        d = math.floor(365.25 * c)
        e = math.floor((b - d) / 30.6001)
        dom = b - d - math.floor(30.6001 * e)
        if e <= 13:
            m = e - 1
            y = c - 4716
        else:
            m = e - 13
            y = c - 4715

        return y, m, dom

    # THEY DEPENDES TO THE PREVIOUS METHODS

    @staticmethod
    def time_mjd_to_utc(timemjd) -> str:
        """
        Convert mjd to utc. Tolerance = 1 s

        Args:
            timemjd (float): time in mjd format

        Returns:
            input converted in utc format (str).
        """
        return AstroUtils.time_tt_to_utc(AstroUtils.time_mjd_to_tt(timemjd))

    @staticmethod
    def time_utc_to_mjd(timeutc):
        """
        Convert mjd to utc. Tolerance = 0.00000001 days

        Args:
            timeutc (str): time in utc format

        Returns:
            input converted in mjd format.
        """
        return AstroUtils.time_tt_to_mjd(AstroUtils.time_utc_to_tt(timeutc))
