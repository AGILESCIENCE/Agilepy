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

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from inspect import signature
from os.path import split, join

from functools import singledispatch
from xml.etree.ElementTree import parse, Element, SubElement, Comment, tostring
from xml.dom import minidom


from agilepy.utils.AstroUtils import AstroUtils
from agilepy.utils.AgilepyLogger import agilepyLogger
from agilepy.config.AgilepyConfig import AgilepyConfig

from agilepy.utils.BooleanExpressionParser import BooleanParser
from agilepy.utils.SourceModel import Source, MultiOutput, Spectrum, SpatialModel, Parameter
from agilepy.utils.CustomExceptions import SourceModelFormatNotSupported, \
                                           FileSourceParsingError, \
                                           SourceNotFound, \
                                           SourcesFileLoadingError, \
                                           SourcesAgileFormatParsingError, \
                                           SourceParamNotFoundError

class SourcesLibrary:

    def __init__(self):
        """
        This method ... blabla ...
        """
        self.logger = agilepyLogger

        self.sourcesFilePath = None
        self.sourcesFilePathPrefix = None
        self.sourcesFilePathFormat = None

        self.sources = None

        self.config = AgilepyConfig()

        self.outdirPath = Path(self.config.getConf("output","outdir")).joinpath("sources_library")

        self.outdirPath.mkdir(parents=True, exist_ok=True)

    def loadSources(self, filePath, fileformat="xml"):
        """
        This method ... blabla ...
        """
        if fileformat not in ["txt", "xml"]:

            raise SourceModelFormatNotSupported("Format {} not supported. Supported formats: txt, xml".format(format))

        self.sourcesFilePathFormat = format
        self.sourcesFilePath = filePath
        self.sourcesFilePathPrefix,_ = split(self.sourcesFilePath)

        if fileformat == "xml":
            self.sources = self._loadFromSourcesXml(self.sourcesFilePath)

        else:
            self.sources = self._loadFromSourcesTxt(self.sourcesFilePath)

        if not self.sources:
            self.logger.critical(self, "Errors during %s parsing (format %s)", self.sourcesFilePath, self.sourcesFilePathFormat)
            raise SourcesFileLoadingError("Errors during {} parsing (format {})".format(self.sourcesFilePath, self.sourcesFilePathFormat))

        for source in self.sources:

            self.updateSourceDistance(source)


        return True

    def writeToFile(self, outfileNamePrefix, fileformat="txt"):
        """
        This method ... blabla ...
        """
        if fileformat not in ["txt", "xml"]:
            raise SourceModelFormatNotSupported("Format {} not supported. Supported formats: txt, xml".format(format))

        outputFilePath = self.outdirPath.joinpath(outfileNamePrefix)

        if fileformat == "txt":
            sourceLibraryToWrite = SourcesLibrary._convertToAgileFormat(self.sources)
            outputFilePath = outputFilePath.with_suffix('.txt')

        else:
            sourceLibraryToWrite = SourcesLibrary._convertToXmlFormat(self.sources)
            outputFilePath = outputFilePath.with_suffix('.xml')

        with open(outputFilePath, "w") as sourceLibraryFile:

            sourceLibraryFile.write(sourceLibraryToWrite)

        self.logger.info(self,"File %s has been produced", outputFilePath)

        return str(outputFilePath)

    def getSources(self):
        """
        This method ... blabla...
        """
        return self.sources

    def getSourcesNames(self):
        """
        This methods ... blabla ...
        """
        return [s.name for s in self.sources]

    def selectSources(self, selection):
        """
        This method ... blablabla..
        """
        userSelectionParamsNames = SourcesLibrary._extractSelectionParams(selection)

        sources = self._getCompatibleSources(userSelectionParamsNames)

        userSelectionParamsMapping = Source._mapSelectionParams(userSelectionParamsNames)


        selected = []

        for source in sources:

            if SourcesLibrary._selectSource(selection, source, userSelectionParamsMapping):

                selected.append(source)

        return selected

    def freeSources(self, selection, parameterName, free):
        """
        Returns the list of sources affected by the update.
        """
        sources = self.selectSources(selection)

        if len(sources) == 0:
            self.logger.warning(self, "No sources have been selected.")
            return []

        free = 1 if free else 0

        affected = []

        for s in sources:

            if s.setFreeAttributeValueOf(parameterName, free):

                affected.append(s)

        return affected

    def deleteSources(self, selection):
        """
        This method ... blabla ...

        returns: the list of the deleted sources
        """
        deletedSources = self.selectSources(selection)

        self.sources = [s for s in self.getSources() if s not in deletedSources]

        return deletedSources

    def parseSourceFile(self, sourceFilePath):
        """
        Static method

        returns: a MultiOutput object
        """
        self.logger.debug(self, "Parsing output file of AG_multi: %s", sourceFilePath)

        with open(sourceFilePath, 'r') as sf:
            lines = sf.readlines()

        body = [line for line in lines if line[0] != "!"]

        if len(body) != 17:
            raise FileSourceParsingError("The number of body lines of the %s source file is not 17."%(sourceFilePath))

        allValues = []

        for lin_num,line in enumerate(body):

            values = line.split(" ")

            values = [v.strip() for v in values if v!='']

            if lin_num == 0:
                values = [v for v in values if v!='[' and v!=']' and v!=',']

            elif lin_num == 5:
                fluxperchannel = values[-1].split(",")
                values = values[:-1]
                values = [*values, fluxperchannel]

            elif lin_num == 8:
                galcoeffs  = line.split(" ")[0].split(",")
                galcoeffserr = [g.strip() for g in line.split(" ")[1].split(",")]
                values = [galcoeffs, galcoeffserr]

            elif lin_num == 9:
                galzerocoeffs  = line.split(" ")[0].split(",")
                galzerocoeffserr = [g.strip() for g in line.split(" ")[1].split(",")]
                values = [galzerocoeffs, galzerocoeffserr]

            elif lin_num == 10:
                isocoeffs  = line.split(" ")[0].split(",")
                isocoeffserr = [g.strip() for g in line.split(" ")[1].split(",")]
                values = [isocoeffs, isocoeffserr]

            elif lin_num == 11:
                isozerocoeffs  = line.split(" ")[0].split(",")
                isozerocoeffserr = [g.strip() for g in line.split(" ")[1].split(",")]
                values = [isozerocoeffs, isozerocoeffserr]

            elif lin_num == 13:
                energybins = line.split(" ")[0].split(",")
                emins = [e.split("..")[0] for e in energybins]
                emaxs = [e.split("..")[1] for e in energybins]
                fovbinnumbers = line.split(" ")[1].split(",")
                fovmin = [e.split("..")[0] for e in fovbinnumbers]
                fovmax = [e.split("..")[1] for e in fovbinnumbers]
                values = [emins, emaxs, fovmin, fovmax, *values[-5:]]


            values = [v for v in values if v!='']

            # print("LINE %d ELEMENTS %d"%(lin_num, len(values)))
            allValues += values

        if len(allValues) != 128:
            self.logger.critical(self, "The values extracted from %s file are lesser then 128", sourceFilePath)
            raise FileSourceParsingError("The values extracted from {} file are lesser then 128".format(sourceFilePath))

        # print("values from .source: ", allValues)

        multiOutput = MultiOutput()

        multiOutput.name.setAttributes(value = allValues[0])

        multiOutput.multiSqrtTS.setAttributes(value = allValues[37])

        multiOutput.multiFlux.setAttributes(value = allValues[53])
        multiOutput.multiFluxErr.setAttributes(value = allValues[54])
        multiOutput.multiFluxPosErr.setAttributes(value = allValues[55])
        multiOutput.multiFluxNegErr.setAttributes(value = allValues[56])

        multiOutput.multiUL.setAttributes(value = allValues[57])

        multiOutput.multiErgLog.setAttributes(value = allValues[64])
        multiOutput.multiErgLogErr.setAttributes(value = allValues[65])


        multiOutput.multiL.setAttributes(value = allValues[41])
        multiOutput.multiB.setAttributes(value = allValues[42])
        multiOutput.multiDistFromStartPosition.setAttributes(value = allValues[43])
        multiOutput.multir.setAttributes(value = allValues[44])
        multiOutput.multia.setAttributes(value = allValues[45])
        multiOutput.multib.setAttributes(value = allValues[46])
        multiOutput.multiphi.setAttributes(value = allValues[47])


        multiOutput.multiStartL.setAttributes(value = allValues[5])
        multiOutput.multiStartB.setAttributes(value = allValues[6])

        multiOutput.multiGalCoeff.setAttributes(value = allValues[89])
        multiOutput.multiGalErr.setAttributes(value = allValues[90])
        multiOutput.multiIsoCoeff.setAttributes(value = allValues[93])
        multiOutput.multiIsoErr.setAttributes(value = allValues[94])


        return multiOutput

    def updateMulti(self, multiOutputData):

        sourcesFound = self.selectSources(lambda name : name == multiOutputData.get("name"))

        if len(sourcesFound) == 0:
            raise SourceNotFound("Source '%s' has not been found in the sources library"%(multiOutputData.get("name")))

        for sourceFound in sourcesFound:


            sourceFound.multi = multiOutputData

            self.updateSourceDistance(sourceFound)

    def updateSourceDistance(self, source):

        mapCenterL = float(self.config.getOptionValue("glon"))
        mapCenterB = float(self.config.getOptionValue("glat"))

        if source.multi:
            sourceL = source.multi.get("multiL")
            sourceB = source.multi.get("multiB")

            if sourceL == -1:
                sourceL = source.multi.get("multiStartL")

            if sourceB == -1:
                sourceB = source.multi.get("multiStartB")

        else:
            pos = source.spatialModel.get("pos")
            sourceL = pos[0]
            sourceB = pos[1]


        self.logger.debug(self, "sourceL %f, sourceB %f, mapCenterL %f, mapCenterB %f", sourceL, sourceB, mapCenterL, mapCenterB)

        dist = AstroUtils.distance(sourceL, sourceB, mapCenterL, mapCenterB)



        if source.multi:
            source.multi.set("multiDist", dist)
            self.logger.debug(self, "'multiDist' parameter of '%s' has been updated from multi: %f", source.multi.get("name"), source.multi.get("multiDist"))
        else:
            source.spatialModel.set("dist", dist)
            self.logger.debug(self, "'dist' parameter of '%s' has been updated from xml: %f", source.name, source.spatialModel.get("dist"))

    def addSource(self, sourceName, sourceDict):

        if not sourceName:
            self.logger.critical(self, "sourceName cannot be None or empty.")
            raise SourceParamNotFoundError("sourceName is a required param.")

        for source in self.sources:
            if sourceName == source.name:
                self.logger.warning(self,"The source %s already exists. Input source will not be added.", sourceName)
                return False

        requiredKeys = ["glon", "glat", "spectrumType"]

        for rK in requiredKeys:
            if rK not in sourceDict:
                self.logger.critical(self, "'%s' is a required param. Please add it to the 'sourceDict' input dictionary", rK)
                raise SourceParamNotFoundError("'{}' is a required param. Please add it to the 'sourceDict' input dictionary".format(rK))

        newSource = Source(sourceName, "PointSource")

        newSource.spatialModel = SpatialModel.getSpatialModelObject("PointSource", 0)
        newSource.spatialModel.set("pos", f'({sourceDict["glon"]}, {sourceDict["glat"]})')

        newSource.spectrum = Spectrum.getSpectrumObject(sourceDict["spectrumType"])

        spectrumKeys = ["flux", "index", "index1", "index2", "cutoffEnergy", "pivotEnergy", "curvature"]

        for sK in spectrumKeys:
            if sK in vars(newSource.spectrum):
                getattr(newSource.spectrum, sK).set(0)
            if sK in sourceDict and sK in vars(newSource.spectrum):
                getattr(newSource.spectrum, sK).set(sourceDict[sK])

        self.sources.append(newSource)

        return True


    @singledispatch
    def _extractSelectionParams(selection):
        raise NotImplementedError('Unsupported type: {}'.format(type(selection)))

    @_extractSelectionParams.register(str)
    def _(selectionString):
        bp = BooleanParser(selectionString)
        return bp.getVARTokens()

    @_extractSelectionParams.register(object)
    def _(selectionLambda):
        return list(signature(selectionLambda).parameters)



    def _getCompatibleSources(self, validatedUserSelectionParams):

        sources = []

        for source in self.sources:

            sourceCompatible = True
            for paramName in validatedUserSelectionParams:


                if not source.isCompatibleWith(paramName):

                    sourceCompatible = False

                    self.logger.warning(self, "The parameter %s cannot be evaluated on source %s because \
                                               the mle() analysis has not been performed yet on that source.", \
                                               paramName, source.name)

            if sourceCompatible:

                sources.append(source)

        return sources


    @staticmethod
    def _selectSource(selection, source, userSelectionParamsMapping):

        selectionParamsValues = [source.getSelectionValue(paramName) for paramName in list(userSelectionParamsMapping.values())]

        return SourcesLibrary.__selectSource(selection, source, userSelectionParamsMapping, selectionParamsValues)

    @singledispatch
    def __selectSource(selection, source, userSelectionParamsMapping, selectionParamsValues):
        raise NotImplementedError('Unsupported type: {}'.format(type(selection)))

    @__selectSource.register(str)
    def _(selectionStr, source, userSelectionParamsMapping, selectionParamsValues):
        bp = BooleanParser(selectionStr)
        variable_dict = dict(zip(userSelectionParamsMapping, selectionParamsValues))
        return bp.evaluate(variable_dict)

    @__selectSource.register(object)
    def _(selectionLambda, source, userSelectionParamsMapping, selectionParamsValues):
        return selectionLambda(*selectionParamsValues)

    def _loadFromSourcesXml(self, xmlFilePath):

        self.logger.debug(self, "Parsing %s ...", xmlFilePath)

        xmlRoot = parse(xmlFilePath).getroot()

        sources = []

        for source in xmlRoot:

            if source.tag != "source":
                SourcesLibrary._fail("Tag <source> expected, %s found."%(source.tag))

            sourceDC = Source(**source.attrib)

            for sourceDescription in source:

                if sourceDescription.tag not in ["spectrum", "spatialModel"]:
                    SourcesLibrary._fail("Tag <spectrum> or <spatialModel> expected, %s found."%(sourceDescr.tag))

                if sourceDescription.tag == "spectrum":
                    sourceDescrDC = Spectrum.getSpectrumObject(sourceDescription.attrib["type"])
                    sourceDescrDC = SourcesLibrary._checkAndAddParameters(sourceDescrDC, sourceDescription)
                    sourceDC.spectrum = sourceDescrDC
                else:
                    sourceDescrDC = SpatialModel.getSpatialModelObject(sourceDescription.attrib["type"], sourceDescription.attrib["locationLimit"])
                    sourceDescrDC = SourcesLibrary._checkAndAddParameters(sourceDescrDC, sourceDescription)
                    sourceDC.spatialModel = sourceDescrDC

            sources.append(sourceDC)

        return sources


    def _loadFromSourcesTxt(self, txtFilePath):

        sources = []

        with open(txtFilePath, "r") as txtFile:

             for line in txtFile:

                 if line == "\n":
                     continue

                 elements = [elem.strip() for elem in line.split(" ") if elem] # each line is a source

                 if len(elements) != 17:
                     self.logger.critical(self, "The number of elements on the line %s is not 17 but %d", line, len(elements))
                     raise SourcesAgileFormatParsingError("The number of elements on the line {} is not 17, but {}".format(line, len(elements)))

                 flux = float(elements[0])
                 glon = elements[1]
                 glat = elements[2]
                 index = float(elements[3])
                 fixflag = int(elements[4])
                 name = elements[6]
                 location_limit = int(elements[7])
                 spectrum_type = int(elements[8])


                 if fixflag == 0:
                     free_bits = [0 for i in range(6)]
                     free_bits_position = 0

                 elif fixflag == 32:
                     free_bits = [0,0,0,0,0,2]
                     free_bits_position = free_bits[5]

                 else:
                     fixflagBinary = f'{fixflag:06b}'
                     free_bits = [int(bit) for bit in reversed(fixflagBinary)]
                     free_bits_position = free_bits[1]


                 sourceDC = Source(name=name, type="PointSource")

                 if spectrum_type == 0:
                     sourceDC.spectrum = Spectrum.getSpectrumObject("PowerLaw")
                 elif spectrum_type == 1:
                     sourceDC.spectrum = Spectrum.getSpectrumObject("PLExpCutoff")
                 elif spectrum_type == 2:
                     sourceDC.spectrum = Spectrum.getSpectrumObject("PLSuperExpCutoff")
                 elif spectrum_type == 3:
                     sourceDC.spectrum = Spectrum.getSpectrumObject("LogParabola")
                 else:
                     self.logger.critical(self,"spectrum_type=%d not supported. Supported: [0,1,2,3]", spectrum_type)
                     raise SourcesAgileFormatParsingError("spectrum_type={} not supported. Supported: [0,1,2,3]".format(spectrum_type))


                 getattr(sourceDC.spectrum, "flux").setAttributes(name="flux", free=free_bits[0], value=flux)

                 if spectrum_type == 0:
                     getattr(sourceDC.spectrum, "index").setAttributes(name="index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))


                 elif spectrum_type == 1:
                     getattr(sourceDC.spectrum, "index").setAttributes(name="index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))

                     getattr(sourceDC.spectrum, "cutoffEnergy").setAttributes(name="cutoffEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14]))

                 elif spectrum_type == 2:
                     getattr(sourceDC.spectrum, "index1").setAttributes(name="index1", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))

                     getattr(sourceDC.spectrum, "cutoffEnergy").setAttributes(name="cutoffEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14]))

                     getattr(sourceDC.spectrum, "index2").setAttributes(name="index2", free=free_bits[4], value=float(elements[10]), \
                                                                        min=float(elements[15]), max=float(elements[16]))

                 elif spectrum_type == 3:
                     getattr(sourceDC.spectrum, "index").setAttributes(name="index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))

                     getattr(sourceDC.spectrum, "pivotEnergy").setAttributes(name="pivotEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14]))

                     getattr(sourceDC.spectrum, "curvature").setAttributes(name="curvature", free=free_bits[4], value=float(elements[10]), \
                                                                        min=float(elements[15]), max=float(elements[16]))


                 sourceDC.spatialModel = SpatialModel.getSpatialModelObject("PointSource", location_limit)

                 getattr(sourceDC.spatialModel, "pos").setAttributes(name="pos", value="(%s,%s)"%(glon, glat), free=free_bits_position)

                 sources.append(sourceDC)

        return sources


    @staticmethod
    def _checkAndAddParameters(sourceDescrDC, sourceDescription):

        for parameter in sourceDescription:

            if parameter.tag != "parameter":
                SourcesLibrary._fail("Tag <parameter> expected, %s found."%(parameter.tag))

            parameterName = parameter.attrib["name"]
            getattr(sourceDescrDC, parameterName).setAttributes(**parameter.attrib)

        return sourceDescrDC


    def _getConf(self, key=None):
        if not key:
            return self.sources
        else: return self.sources[key]


    @staticmethod
    def _fail(msg):
        raise FileSourceParsingError("File source parsing failed: {}".format(msg))

    @staticmethod
    def _convertToAgileFormat(sources):

        sourceStr = ""

        for source in sources:

            # get flux value
            if source.multi:
                flux = source.multi.get("multiFlux")
            else:
                flux = source.spectrum.get("flux")

            sourceStr += str(flux)+" "

            # glon e glat
            pos = source.spatialModel.get("pos")
            glon = pos[0]
            glat = pos[1]
            sourceStr += str(glon) + " "
            sourceStr += str(glat) + " "


            if source.spectrum.stype == "PLSuperExpCutoff":
                index1 = source.spectrum.get("index1")
                sourceStr += str(index1) + " "
            else:
                index = source.spectrum.get("index")
                sourceStr += str(index) + " "

            sourceStr += SourcesLibrary._computeFixFlag(source, source.spectrum.stype)+" "

            sourceStr += "2 "

            sourceStr += source.name + " "

            sourceStr += str(source.spatialModel.locationLimit) + " "


            if source.spectrum.stype == "PowerLaw":
                sourceStr += "0 0 0 "

            elif source.spectrum.stype == "PLExpCutoff":
                cutoffenergy = source.spectrum.get("cutoffEnergy", strRepr=True)
                sourceStr += "1 "+str(cutoffenergy)+" 0 "

            elif source.spectrum.stype == "PLSuperExpCutoff":
                cutoffenergy = source.spectrum.get("cutoffEnergy", strRepr=True)
                index2 = source.spectrum.get("index2", strRepr=True)
                sourceStr += "2 "+str(cutoffenergy)+" "+str(index2)+" "

            else:
                pivotenergy = source.spectrum.get("pivotEnergy", strRepr=True)
                curvature = source.spectrum.get("curvature", strRepr=True)
                sourceStr += "3 "+str(pivotenergy)+" "+str(curvature)+" "



            if source.spectrum.stype == "PLSuperExpCutoff":
                sourceStr += str(source.spectrum.index1.min) + " " + \
                             str(source.spectrum.index1.max)+ " "
            else:
                sourceStr += str(source.spectrum.index.min) + " " + \
                             str(source.spectrum.index.max) + " "


            if source.spectrum.stype == "PowerLaw":
                sourceStr += "-1 -1 -1 -1"

            elif source.spectrum.stype == "PLExpCutoff":
                sourceStr += str(source.spectrum.cutoffEnergy.min) +" " \
                           + str(source.spectrum.cutoffEnergy.max) +" "\
                           + " -1 -1"

            elif source.spectrum.stype == "PLSuperExpCutoff":
                sourceStr += str(source.spectrum.cutoffEnergy.min) +" "\
                           + str(source.spectrum.cutoffEnergy.max) +" "\
                           + str(source.spectrum.index2.min) +" "\
                           + str(source.spectrum.index2.max)

            else:
                sourceStr += str(source.spectrum.pivotEnergy.min) +" "\
                           + str(source.spectrum.pivotEnergy.max) +" "\
                           + str(source.spectrum.curvature.min) +" "\
                           + str(source.spectrum.curvature.max)


            sourceStr += "\n"

        return sourceStr

    @staticmethod
    def _convertToXmlFormat(sources):
        """
        https://pymotw.com/2/xml/etree/ElementTree/create.html
        """
        root = Element('source_library', title="source library")

        for source in sources:

            source_tag = SubElement(root, "source", {"name": source.name, "type": source.type})


            spectrum_tag = Element("spectrum", {"type": source.spectrum.stype})

            for parameterDict in source.spectrum.getParameterDict():

                param_tag = Element("parameter", parameterDict)
                spectrum_tag.append(param_tag)

            source_tag.append(spectrum_tag)



            spatial_model_tag = Element("spatialModel", { "type": source.spatialModel.sptype, \
                                                          "location_limit": str(source.spatialModel.locationLimit) })

            for parameterDict in source.spatialModel.getParameterDict():

                param_tag = Element("parameter", parameterDict)
                spatial_model_tag.append(param_tag)

            source_tag.append(spatial_model_tag)


        rough_string = tostring(root, 'utf-8')

        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent="  ")



    @staticmethod
    def _computeFixFlag(source, spectrumType):

        indexFree = ""
        index1Free = ""
        index2Free = ""
        curvatureFree = ""
        cutoffEnergyFree = ""
        pivotEnergyFree = ""
        posFree = ""

        posFree = source.spatialModel.getFree("pos", strRepr=True)
        fluxFree = source.spectrum.getFree("flux", strRepr=True)


        if spectrumType == "PowerLaw":
            indexFree = source.spectrum.getFree("index", strRepr=True)

        elif spectrumType == "PLExpCutoff":
            indexFree = source.spectrum.getFree("index", strRepr=True)

            cutoffEnergyFree = source.spectrum.getFree("cutoffEnergy", strRepr=True)

        elif spectrumType == "PLSuperExpCutoff":
            index1Free = source.spectrum.getFree("index1", strRepr=True)
            cutoffEnergyFree = source.spectrum.getFree("cutoffEnergy", strRepr=True)
            index2Free = source.spectrum.getFree("index2", strRepr=True)

        else:
            indexFree = source.spectrum.getFree("index", strRepr=True)
            pivotEnergyFree = source.spectrum.getFree("pivotEnergy", strRepr=True)
            curvatureFree = source.spectrum.getFree("curvature", strRepr=True)

        if source.spectrum.getFree("flux") == 0:
            return "0"

        if source.spatialModel.getFree("pos") == 2:

            bitmask = posFree + \
                      curvatureFree + index2Free + \
                      cutoffEnergyFree + pivotEnergyFree + \
                      indexFree + index1Free + \
                      "0" + \
                      fluxFree

        else:

            bitmask = curvatureFree + index2Free + \
                      cutoffEnergyFree + pivotEnergyFree + \
                      indexFree + index1Free + \
                      posFree + \
                      fluxFree

        #print("bitmask:\n",bitmask)
        # '{0:08b}'.format(6)
        fixflag = int(bitmask, 2)
        #print("fixflag: ",fixflag)

        return str(fixflag)
