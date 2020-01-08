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
from os.path import split, join


from agilepy.dataclasses.Source import *
from agilepy.utils.Utils import AgilepyLogger

class SourcesConfig:
    """

    """
    def __init__(self, configurationFilePath):

        self.configurationFilePath = configurationFilePath
        self.configurationFilePathPrefix,_ = split(self.configurationFilePath)

        self.sourcesConfig = self.parseSourceXml()

        self.sourcesConfigAgileFormat = self.convertToAgileFormat()

        self.logger = AgilepyLogger()


    def parseSourceXml(self):

        xmlRoot = ET.parse(self.configurationFilePath).getroot()

        sourceConfig = SourceLibrary(**xmlRoot.attrib, sources=[])

        for source in xmlRoot:

            if source.tag != "source":
                self.fail("Tag <source> expected, %s found."%(source.tag))

            sourceDC = Source(**source.attrib)

            for sourceDescription in source:

                if sourceDescription.tag not in ["spectrum", "spatialModel"]:
                    self.fail("Tag <spectrum> or <spatialModel> expected, %s found."%(sourceDescr.tag))

                if sourceDescription.tag == "spectrum":
                    sourceDescrDC = Spectrum(**sourceDescription.attrib, parameters=[])
                    sourceDescrDC = self.checkAndAddParameters(sourceDescrDC, sourceDescription)
                    sourceDC.spectrum = sourceDescrDC
                else:
                    sourceDescrDC = SpatialModel(**sourceDescription.attrib, parameters=[])
                    sourceDescrDC = self.checkAndAddParameters(sourceDescrDC, sourceDescription)
                    sourceDC.spatialModel = sourceDescrDC


            sourceConfig.sources.append(sourceDC)

        return sourceConfig

    def checkAndAddParameters(self, sourceDescrDC, sourceDescription):
        for parameter in sourceDescription:

            if parameter.tag != "parameter":
                self.fail("Tag <parameter> expected, %s found."%(parameter.tag))

            paramDC = Parameter(**parameter.attrib)

            sourceDescrDC.parameters.append(paramDC)

        return sourceDescrDC

    def getConf(self, key=None):
        if not key:
            return self.sourcesConfig
        else: return self.sourcesConfig[key]

    def fail(self, msg):
        print("[SourcesConfig] Parsing failed: {}".format(self.configurationFilePath, e))
        exit(1)

    def convertToAgileFormat(self):

        outfilepath = join(self.configurationFilePathPrefix,"agileSources.txt")


        with open(outfilepath, "w") as agileConf:

            sourceStr = ""

            for source in self.sourcesConfig.sources:

                # get flux value
                flux = [param.value for param in source.spectrum.parameters if param.name == "Flux"].pop()
                sourceStr += flux+" "

                # glon e glat
                sourceStr += source.spatialModel.getParamAttributeWhere("value", "name", "GLON") + " "
                sourceStr += source.spatialModel.getParamAttributeWhere("value", "name", "GLAT") + " "

                if source.spectrum.type == "PLSuperExpCutoff":
                    sourceStr += source.spectrum.getParamAttributeWhere("value", "name", "Index1") + " "
                else:
                    sourceStr += source.spectrum.getParamAttributeWhere("value", "name", "Index") + " "

                sourceStr += self.computeFixFlag(source)+" "

                sourceStr += "2 "

                sourceStr += source.name + " "

                sourceStr += source.spatialModel.location_limit + " "


                if source.spectrum.type == "PowerLaw":
                    sourceStr += "0 0 0 "

                elif source.spectrum.type == "PLExpCutoff":
                    cutoffenergy = source.spectrum.getParamAttributeWhere("value", "name", "CutoffEnergy")
                    sourceStr += "1 "+str(cutoffenergy)+" 0 "

                elif source.spectrum.type == "PLSuperExpCutoff":
                    cutoffenergy = source.spectrum.getParamAttributeWhere("value", "name", "CutoffEnergy")
                    index2 = source.spectrum.getParamAttributeWhere("value", "name", "Index2")
                    sourceStr += "2 "+str(cutoffenergy)+" "+str(index2)+" "

                else:
                    pivotenergy = source.spectrum.getParamAttributeWhere("value", "name", "PivotEnergy")
                    curvature = source.spectrum.getParamAttributeWhere("value", "name", "Curvature")
                    sourceStr += "3 "+str(pivotenergy)+" "+str(curvature)+" "



                if source.spectrum.type == "PLSuperExpCutoff":
                    sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "Index1") + " " + source.spectrum.getParamAttributeWhere("max", "name", "Index1") + " "
                else:
                    sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "Index") + " " + source.spectrum.getParamAttributeWhere("max", "name", "Index") + " "


                if source.spectrum.type == "PowerLaw":
                    sourceStr += "-1 -1 -1 -1"

                elif source.spectrum.type == "PLExpCutoff":
                    sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "CutoffEnergy") +" "\
                               + source.spectrum.getParamAttributeWhere("max", "name", "CutoffEnergy") +" "\
                               + " -1 -1"

                elif source.spectrum.type == "PLSuperExpCutoff":
                    sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "CutoffEnergy") +" "\
                               + source.spectrum.getParamAttributeWhere("max", "name", "CutoffEnergy") +" "\
                               + source.spectrum.getParamAttributeWhere("min", "name", "Index2") +" "\
                               + source.spectrum.getParamAttributeWhere("max", "name", "Index2")

                else:
                    sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "PivotEnergy") +" "\
                               + source.spectrum.getParamAttributeWhere("max", "name", "PivotEnergy") +" "\
                               + source.spectrum.getParamAttributeWhere("min", "name", "Curvature") +" "\
                               + source.spectrum.getParamAttributeWhere("max", "name", "Curvature")


                sourceStr += "\n"


            agileConf.write(sourceStr)

        # self.logger.info("Sources configuration in AGILE format placed at: %s", outfilepath)


    def computeFixFlag(self, source):
        if source.spectrum.getFreeAttributeValueOf("name", "Flux") == 0:
            return "0"

        if source.spatialModel.free == 2:

            bitmask = source.spatialModel.free + \
                      source.spectrum.getFreeAttributeValueOf("name", "Curvature") + source.spectrum.getFreeAttributeValueOf("name", "Index2") + \
                      source.spectrum.getFreeAttributeValueOf("name", "CutoffEnergy") + source.spectrum.getFreeAttributeValueOf("name", "PivotEnergy") + \
                      source.spectrum.getFreeAttributeValueOf("name", "Index") + source.spectrum.getFreeAttributeValueOf("name", "Index1") + \
                      "0" + \
                      source.spectrum.getFreeAttributeValueOf("name", "Flux")

        else:
            bitmask = source.spectrum.getFreeAttributeValueOf("name", "Curvature") + source.spectrum.getFreeAttributeValueOf("name", "Index2") + \
                      source.spectrum.getFreeAttributeValueOf("name", "CutoffEnergy") + source.spectrum.getFreeAttributeValueOf("name", "PivotEnergy") + \
                      source.spectrum.getFreeAttributeValueOf("name", "Index") + source.spectrum.getFreeAttributeValueOf("name", "Index1") + \
                      source.spatialModel.free + \
                      source.spectrum.getFreeAttributeValueOf("name", "Flux")

        #print("bitmask:\n",bitmask)
        # '{0:08b}'.format(6)
        fixflag = int(bitmask, 2)
        #print("fixflag: ",fixflag)

        return str(fixflag)
