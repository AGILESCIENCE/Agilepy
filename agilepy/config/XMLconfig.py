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

import xml.etree.ElementTree as ET
from agilepy.dataclasses.Source import *

class SourcesConfig:
    """

    """
    def __init__(self, configurationFilePath):

        self.configurationFilePath = configurationFilePath

        self.sourcesConfig = {}
        self.sourcesConfigAgileFormat = {}

        self.parseSourceXml()

        self.convertToAgileFormat()



    def parseSourceXml(self):

        xmlRoot = ET.parse(self.configurationFilePath).getroot()

        sourceConfig = SourceLibrary([], xmlRoot.attrib["title"])

        for source in xmlRoot:

            if source.tag != "source":
                self.fail("Tag <source> expected, %s found."%(source.tag))

            sourceDC = Source([], source.attrib["name"], source.attrib["type"])

            for sourceDescr in source:

                if sourceDescr.tag not in ["spectrum", "spatialModel"]:
                    self.fail("Tag <spectrum> or <spatialModel> expected, %s found."%(sourceDescr.tag))

                sourceDescrDC = SourceDescription([], sourceDescr.tag, sourceDescr.attrib["type"])

                for parameter in sourceDescr:

                    if parameter.tag != "parameter":
                        self.fail("Tag <parameter> expected, %s found."%(parameter.tag))

                    paramDC = Parameter(**parameter.attrib)

                    sourceDescrDC.parameters.append(paramDC)

                sourceDC.SourceDescription.append(sourceDescrDC)

            sourceConfig.sources.append(sourceDC)

        return sourceConfig


    def convertToAgileFormat(self):
        pass

    def getConf(self, key=None):
        if not key:
            return self.sourcesConfig
        else: return self.sourcesConfig[key]

    def fail(self, msg):
        print("[SourcesConfig] Parsing failed: {}".format(self.configurationFilePath, e))
        exit(1)
