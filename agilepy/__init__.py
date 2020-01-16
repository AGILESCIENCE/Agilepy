"""
 DESCRIPTION
       Agilepy software

 NOTICE
       Any information contained in this software
       is property of the AGILE TEAM and is strictly
       private and confidential.
       Copyright (C) 2005-2020 AGILE Team.
           Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
           Addis Antonio <antonio.addis@inaf.it>
           Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
           Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
       All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import os

if "AGILE" not in os.environ:
    print("\nPlease, set $AGILE.\n")
    exit(1)

if "agile-B25-r5-cat2-B5" not in os.environ["AGILE"]:
    print("\nPlease, load the 'agile-B25-r5-cat2-B5' AGILE environment:\n\n >>source /opt/module/agile-B25-r5-cat2-B5\n")
    exit(1)

if "PFILES" not in os.environ:
    print("\nPlease, set PFILES environment variable:\n\n >>export PFILES=.\n")
    exit(1)
