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
# import julian

class AstroUtils:

    @staticmethod
    def distance(ll, bl, lf, bf):

        if ll < 0 or ll > 360 or lf < 0 or lf > 360:
            return -2
        elif bl < -90 or bl > 90 or bf < -90 or bf > 90:
            return -2
        else:
            d1 = bl - bf
            d2 = ll - lf;

            bl1 = math.pi / 2.0 - (bl * math.pi / 180.0)
            bf1 = math.pi / 2.0 - (bf * math.pi / 180.0)
            m4 = math.cos(bl1) * math.cos(bf1) + math.sin(bl1) * math.sin(bf1) * math.cos(d2 * math.pi / 180.0);
            if m4 > 1:
                m4 = 1

            try:
                return math.acos(m4) * 180.0 / math.pi;

            except Exception as e:

                print("\nException in AstroUtils.distance (error in acos() ): ", e)

                return math.sqrt(d1 * d1 + d2 * d2);


    # BASIC CONVERSIONS
    @staticmethod
    def time_mjd_to_tt(timemjd):
        return (timemjd - 53005.0) * 86400.0

    @staticmethod
    def time_tt_to_mjd(timett):
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
    def time_tt_to_utc(time):

        utc_offset = 2400000.5
        mjdref = 53005.0
        sod = 86400.0
        sec_offset = 43200.0

        a = AstroUtils.jd_to_civil(utc_offset + mjdref + ( (time + sec_offset)/sod ))
        print("jd_to_civil:",a)
        b = AstroUtils.day_fraction_to_time(a[2] % 1)
        print("day_fraction_to_time:",b)
        # utc = [a[0] , a[1] , float(int(a[2])), b[0] , b[1] , b[2] , b[3]]
        utc_s = "%s-%02d-%02dT%02d:%02d:%02d"%(str(a[0]), int(a[1]), int(a[2]), b[0], b[1], b[2])
        return utc_s

    """
    @staticmethod
    def time_utc_to_tt(utc):

        ls1 = utc.split("T")[0];
        ls2 = utc.split("T")[1];
        year=ls1.split("-")[0];
        month=ls1.split("-")[1];
        day=ls1.split("-")[2];
        hour=ls2.split(":")[0];
        min=ls2.split(":")[1];
        sec=ls2.split(":")[2];

        utc_offset = 2400000.5
        mjdref = 53005.0
        sod = 86400.0
        sec_offset = 43200.0
        fod = AstroUtils.time_to_day_fraction( int(hour) , int(min) , int(sec) )

        dt = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S')

        jd = julian.to_jd(dt, fmt='jd')
        #print("jd:\n",jd)

        jd = jd + fod
        #print("jd:\n",jd)

        tt = (jd - utc_offset - mjdref) * sod
        #print("tt:\n",tt)

        tt -= sec_offset

        return tt
    """

    # Convert a fractional day +fr+ to [hours, minutes, seconds,
    # fraction_of_a_second]
    @staticmethod
    def day_fraction_to_time(fr):
        ss,  fr = divmod(fr, 1/86400)
        h,   ss = divmod(ss, 3600)
        min, s  = divmod(ss, 60)
        return h, min, s, fr

    @staticmethod
    def time_to_day_fraction(h, min, s):
        return (h * 3600 + min * 60 + s)/86400


    @staticmethod
    def jd_to_civil(jd): #. sg=Date::GREGORIAN):
        """
        Convert a Julian Day Number to a Civil Date.  +jd+ is
        the Julian Day Number. +sg+ specifies the Day of
        Calendar Reform.
        Returns the corresponding [year, month, day_of_month]
        as a three-element array.
        if isJulian(jd, sg):
        a = jd
        else:
        x = math.floor((jd - 1867216.25) / 36524.25)
        a = jd + 1 + x - math.floor(x / 4.0)
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


    """
    @staticmethod
	def julian? (jd, sg)
		case sg
		when Numeric
			jd < sg
		else
			not sg
		end
	end
	"""

    # THEY DEPENDES TO THE PREVIOUS METHODS

    @staticmethod
    def time_mjd_to_utc(mjd):
        return AstroUtils.time_tt_to_utc(AstroUtils.time_mjd_to_tt(mjd))

    """
    @staticmethod
    def time_utc_to_mjd(utc):
        return AstroUtils.time_tt_to_mjd(AstroUtils.time_utc_to_tt(utc))
    """
