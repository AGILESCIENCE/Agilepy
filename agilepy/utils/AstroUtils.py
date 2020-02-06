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

    @staticmethod
    def time_mjd_to_tt(timemjd):
        return (timemjd - 53005.0) * 86400.0

    @staticmethod
    def time_tt_to_mjd(timett):
        return (timett / 86400.0) + 53005.0
