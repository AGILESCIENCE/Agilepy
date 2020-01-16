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


import unittest

from agilepy.api.SourcesLibrary import SourcesLibrary
from agilepy.dataclasses.Source import MultiOutput

class SourcesLibraryUnittesting(unittest.TestCase):

   def test_source_file_parsing(self):

       sl = SourcesLibrary()

       res = sl.parseSourceFile("./agilepy/testing/unittesting/api/data/multi.multimaps.source")
       self.assertEqual(True, bool(res))

       res = sl.parseSourceFile("./agilepy/testing/unittesting/api/data/multi.source")
       self.assertEqual(True, bool(res))

       res = sl.parseSourceFile("./agilepy/testing/unittesting/api/data/testcase1_2AGLJ0835-4514.source")
       self.assertEqual(True, bool(res))


if __name__ == '__main__':
    unittest.main()
