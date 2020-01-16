"""
 DESCRIPTION
       Agilepy software

 NOTICE
       Any information contained in this software
       is property of the AGILE TEAM and is strictly
       private and confidential.
       Copyright (C) 2005-2020 AGILE Team.
           Addis Antonio <antonio.addis@inaf.it>
           Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
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

from agilepy.api import AGAnalysis, SourcesLibrary, ScienceTools


aga = AGAnalysis("./agilepy/testing/demo/examples/conf.yaml", "/tmp/agilepy_test/Agilepy/agilepy/testing/demo/examples/sourceconf.xml")

aga.setOptions(binsize=99999)
aga.printOptions("maps")
aga.resetConf()
aga.printOptions("maps")


# Usage of the SourcesLibrary class
sourcesLib = aga.getSourcesLibrary()

sources = sourcesLib.selectSourcesWithLambda(lambda Name : Name == "2AGLJ0835-4514")
for s in sources:
    print("\nSource found!")
    print(s)

print("\n\n")



# mimic mle()
#data = ScienceTools.multi.parseOutputFile()
#sourcesLib._updateMulti(data)

maplistFilePath = aga.generateMaps()

print("\n\nMaplist file: ", maplistFilePath)

aga.mle(maplistFilePath)



# sources = aga.freeSources("Name == '2AGLJ0835-4514' and Dist > 0 and Flux > 0", "Flux", False)

sources = aga.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ0835-4514" and Dist > 0 and Flux > 0, "Flux", False)
print("\n\nSource with Flux NOT freed: " )
for s in sources:
    print(s)

sources = aga.freeSources(lambda Name, Dist, Flux : Name == "2AGLJ0835-4514" and Dist > 0 and Flux > 0, "Flux", True)
print("\n\nSource with Flux freed: " )
for s in sources:
    print(s)


print("\n\nNumber of sources: ", len(sourcesLib.getSources()))


deleted = aga.deleteSources(lambda Name, Dist, Flux : Name == "2AGLJ0835-4514" and Dist > 0 and Flux > 0)
print("\n\nDeleted sources:")
for s in deleted:
    print(s)


print("\n\nNumber of sources: ", len(sourcesLib.getSources()))
