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
from os.path import splitext
from os import listdir
from copy import deepcopy

from functools import singledispatch
from xml.etree.ElementTree import parse, Element, SubElement, Comment, tostring
from xml.dom import minidom

from agilepy.core.Parameters import Parameters
from agilepy.core.SourceModel import Source, MultiOutput, Spectrum, SpatialModel, Parameter
from agilepy.core.CustomExceptions import   SourceModelFormatNotSupported, \
                                            FileSourceParsingError, \
                                            SourceNotFound, \
                                            SourcesFileLoadingError, \
                                            SourcesAgileFormatParsingError, \
                                            SourceParamNotFoundError, \
                                            MultiOutputNotFoundError
from agilepy.utils.BooleanExpressionParser import BooleanParser
from agilepy.utils.Utils import Utils
from agilepy.utils.AstroUtils import AstroUtils

class SourcesLibrary:

    def __init__(self, agilepyConfig, agilepyLogger):
        """
        This method ... blabla ...
        """
        self.logger = agilepyLogger

        self.config = agilepyConfig

        self.sources = []

        self.sourcesBKP = None

        self.outdirPath = Path(self.config.getConf("output","outdir")).joinpath("sources_library")

        self.outdirPath.mkdir(parents=True, exist_ok=True)

    def backupSL(self):
        self.sourcesBKP = deepcopy(self.sources)

    def restoreSL(self):
        self.sources = self.sourcesBKP

    def destroy(self):
        self.sources = []
        self.sourcesBKP = None
        self.outdirPath = None

    def loadSourcesFromCatalog(self, catalogName, rangeDist = (0, float("inf")), show=False):

        supportedCatalogs = ["2AGL"]
        scaleFlux = False


        if catalogName == "2AGL":
            catPath = Utils._expandEnvVar("$AGILE/catalogs/2AGL.xml")
            if not Path(catPath).exists():
                catPath = Utils._expandEnvVar("$AGILE/catalogs/2AGL.multi")

            cat2Emin, cat2Emax = Parameters.getCat2EminEmax()
            uEmin = self.config.getOptionValue("emin")
            uEmax = self.config.getOptionValue("emax")

            if cat2Emin != uEmin or cat2Emax != uEmax:
                scaleFlux = True
                self.logger.info(self, f"The input energy range ({uEmin},{uEmax}) is different to the CAT2 energy range ({cat2Emin},{cat2Emax}). A scaling of the sources flux will be performed.")

        elif catalogName == "4FGL":

            scaleFlux = False
            raise FileNotFoundError(f"The catalog {catalogName} is going to be supported soon. Supported catalogs: {supportedCatalogs}")

        else:
            self.logger.critical(self, "The catalog %s is not supported. Supported catalogs: %s", catalogName, ' '.join(supportedCatalogs))
            raise FileNotFoundError(f"The catalog {catalogName} is not supported. Supported catalogs: {supportedCatalogs}")

        return self.loadSourcesFromFile(catPath, rangeDist, scaleFlux = scaleFlux, show = show)

    def loadSourcesFromFile(self, filePath, rangeDist = (0, float("inf")), scaleFlux = False, show=False):

        filePath = Utils._expandEnvVar(filePath)

        _, fileExtension = splitext(filePath)

        supportFormats = [".txt", ".xml", ".multi"]

        if fileExtension not in supportFormats:

            raise SourceModelFormatNotSupported("Format of {} not supported. Supported formats: {}".format(filePath, ' '.join(supportFormats)))


        if fileExtension == ".xml":
            newSources = self._loadFromSourcesXml(filePath)

        elif fileExtension == ".txt" or fileExtension == ".multi":
            newSources = self._loadFromSourcesTxt(filePath)


        if newSources is None:
            self.logger.critical(self, "Errors during %s parsing (%s)", filePath, fileExtension)
            raise SourcesFileLoadingError("Errors during {} parsing ({})".format(filePath, fileExtension))

        addedSources = []

        newSources = [source for source in self._filterByDistance(newSources, rangeDist)]

        addedSources = [source for source in self._addSourcesGenerator(newSources)]

        if scaleFlux:

            addedSources = [source for source in self._scaleSourcesFlux(addedSources)]

        if show:
            for s in addedSources:
                print(f"{s}")
                # self.logger.info(self, f"{s}")

        self.logger.info(self, "Loaded %d sources. Total sources: %d", len(addedSources), len(self.sources))

        return addedSources

    def convertCatalogToXml(self, catalogFilepath):

        catalogFilepath = Utils._expandEnvVar(catalogFilepath)

        filename, fileExtension = splitext(catalogFilepath)

        supportedFormats = [".multi", ".txt"]
        if fileExtension not in supportedFormats:
            raise SourceModelFormatNotSupported("Format of {} not supported. Supported formats: {}".format(catalogFilepath, ' '.join(supportedFormats)))

        newSources = self._loadFromSourcesTxt(catalogFilepath)

        return self.writeToFile(filename, fileformat="xml", sources=newSources)

    def writeToFile(self, outfileNamePrefix, fileformat="txt", sources=None):

        if fileformat not in ["txt", "xml", "reg"]:
            raise SourceModelFormatNotSupported("Format {} not supported. Supported formats: txt, xml, reg".format(format))

        outputFilePath = self.outdirPath.joinpath(outfileNamePrefix)

        if sources is None:
            sources = self.sources

        if len(sources) == 0:
            self.logger.info(self,"No sources have been loaded yet. No file has been produced.")
            return ""

        if fileformat == "txt":
            sourceLibraryToWrite = self._convertToAgileFormat(sources)
            outputFilePath = outputFilePath.with_suffix('.txt')

        elif fileformat == "xml":
            sourceLibraryToWrite = self._convertToXmlFormat(sources)
            outputFilePath = outputFilePath.with_suffix('.xml')

        elif fileformat == "reg":
            sourceLibraryToWrite = self._convertToRegFormat(sources)
            outputFilePath = outputFilePath.with_suffix('.reg')

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

    def selectSources(self, selection, show=False):
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

        if show:
            for s in selected:
                print(f"{s}")
                # self.logger.info(self, f"{s}")

        return selected

    def fixSource(self, source):
        """
        Set to False all freeable params of a source
        """
        affected = False

        freeableParams = Source.freeParams["spectrum"] + Source.freeParams["spatialModel"]

        for paramName in freeableParams:

            if source.setFreeAttributeValueOf(paramName, False):
                affected = True

        return affected

    def freeSources(self, selection, parameterName, free, show=False):
        """
        Returns the list of sources affected by the update.
        """
        sources = self.selectSources(selection, show=False)

        if len(sources) == 0:
            self.logger.warning(self, "No sources have been selected.")
            return []

        free = 1 if free else 0

        affected = []

        for s in sources:

            if s.setFreeAttributeValueOf(parameterName, free):

                affected.append(s)

                if show:
                    print(f"{s}")
                    # self.logger.info(self, f"{s}")

        return affected

    def deleteSources(self, selection, show = False):
        """
        This method ... blabla ...

        returns: the list of the deleted sources
        """
        deletedSources = self.selectSources(selection, show=False)

        self.sources = [s for s in self.getSources() if s not in deletedSources]

        if show:
            for s in deletedSources:
                print(f"{s}")
                # self.logger.info(self, f"{s}")

        self.logger.info(self, "Deleted %d sources.", len(deletedSources))
        return deletedSources

    """
    def updateSourceParameter(self, sourceName, parameterName, parameterValue):
    
        sources = self.selectSources(lambda name : name == sourceName, show=False)

        if len(sources) == 0:
            raise SourceNotFound(f"Source '{sourceName}' has not been found in the sources library")

        source = sources.pop()

        # it will update 'position' and 'distance'
        if parameterName == "pos":

            if type(parameterValue) != tuple:
                raise ValueError(f"In order to update the 'pos' parameter you must pass a tuple (glan, glon).")

            oldPos = source.spatialModel.pos

            glon = parameterValue[0]
            glat = parameterValue[1]

            newPos = Parameter("pos", "tuple<float,float>")
            newPos.setAttributes(value = f"({glon}, {glat})", free = source.spatialModel.pos.free)

            source.spatialModel.pos = newPos

            if oldPos.value != newPos.value:
                newDistance = self.getSourceDistance(source)
                source.spatialModel.dist.setAttributes(value = newDistance)
                self.logger.info(self, f"Old position is {oldPos.value}, new position is {source.spatialModel.pos.value}, new distance is {source.spatialModel.dist}")
                return True
            else:
                self.logger.info(self, f"Position is not changed: {source.spatialModel.pos.value}")
                return False
    """
    


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

        multiOutput.multiStartL.setAttributes(value = allValues[5])
        multiOutput.multiStartB.setAttributes(value = allValues[6])

        multiOutput.multiSqrtTS.setAttributes(value = allValues[37])

        multiOutput.multiFlux.setAttributes(value = allValues[53])
        multiOutput.multiFluxErr.setAttributes(value = allValues[54])
        multiOutput.multiFluxPosErr.setAttributes(value = allValues[55])
        multiOutput.multiFluxNegErr.setAttributes(value = allValues[56])

        multiOutput.multiUL.setAttributes(value = allValues[57])

        multiOutput.multiExp.setAttributes(value = allValues[59])


        multiOutput.multiErgLog.setAttributes(value = allValues[64])
        multiOutput.multiErgLogErr.setAttributes(value = allValues[65])

        multiOutput.multiLPeak.setAttributes(value = allValues[38])
        multiOutput.multiBPeak.setAttributes(value = allValues[39])
        multiOutput.multiDistFromStartPositionPeak.setAttributes(value = allValues[40])

        multiOutput.multiL.setAttributes(value = allValues[41])
        multiOutput.multiB.setAttributes(value = allValues[42])
        multiOutput.multiDistFromStartPosition.setAttributes(value = allValues[43])
        multiOutput.multir.setAttributes(value = allValues[44])
        multiOutput.multia.setAttributes(value = allValues[45])
        multiOutput.multib.setAttributes(value = allValues[46])
        multiOutput.multiphi.setAttributes(value = allValues[47])

        multiOutput.multiIndex.setAttributes(value = allValues[69])
        multiOutput.multiPar2.setAttributes(value = allValues[71])
        multiOutput.multiPar3.setAttributes(value = allValues[73])

        multiOutput.multiGalCoeff.setAttributes(value = allValues[89])
        multiOutput.multiGalErr.setAttributes(value = allValues[90])
        multiOutput.multiIsoCoeff.setAttributes(value = allValues[93])
        multiOutput.multiIsoErr.setAttributes(value = allValues[94])

        multiOutput.startDataTT.setAttributes(value = allValues[99])
        multiOutput.endDataTT.setAttributes(value = allValues[100])

        multiOutput.multiExpRatio.setAttributes(value = allValues[109])


        return multiOutput

    def updateSourcePosition(self, sourceName, glon, glat):
        
        sources = self.selectSources(lambda name : name == sourceName, show=False)

        if len(sources) == 0:
            raise SourceNotFound(f"Source '{sourceName}' has not been found in the sources library")
        
        if len(sources) > 1:
            self.logger.warning(self, f"Found more than one source:{sources}")

        source = sources.pop()

        if glat < -90 or glat > 90:
            raise ValueError(f"glat={glat}")
        
        if glon < 0 or glon > 360:
            raise ValueError(f"glon={glon}")

        newPos = Parameter("pos", "tuple<float,float>")
        newPos.setAttributes(value = f"({glon}, {glat})", free = source.spatialModel.pos.free)
        source.spatialModel.pos = newPos

        newDistance = self.getSourceDistance(source)
        source.spatialModel.set("dist", newDistance)



    def updateMulti(self, multiOutputData):

        sources = self.selectSources(lambda name : name == multiOutputData.get("name"), show=False)

        if len(sources) == 0:
            raise SourceNotFound(f"Source '{multiOutputData.get('name')}' has not been found in the sources library")
        
        if len(sources) > 1:
            self.logger.warning(self, f"Found more than one source:{sources}")

        for source in sources:

            source.multi = multiOutputData

            freeParams = source.getFreeParams()

            self.logger.info(self, f"{multiOutputData.get('name')} (free) parameters update after mle: {freeParams}")

            if "pos" in freeParams:
                freeParams.remove("pos")

            # updating 'spectrum' params
            mapping = {
                "flux" : "multiFlux",
                "index" : "multiIndex",
                "cutoffEnergy" : "multiPar2",
                "pivotEnergy" : "multiPar2",
                "index2" : "multiPar3",
                "curvature" : "multiPar3",
            }

            for paramName in freeParams:
                newVal = source.multi.get(mapping[paramName])
                oldVal = source.spectrum.get(paramName)
                if newVal != oldVal:
                    source.spectrum.set(paramName, newVal)
                    self.logger.info(self, f"'{paramName}' parameter has been updated: {oldVal}==>{newVal}")
                else:
                    self.logger.info(self, f"'{paramName}' parameter has not changed: {oldVal}==>{newVal}")


            if source.multi.get("multiL") != -1 and source.multi.get("multiB") != -1:
                oldPos = source.spatialModel.get("pos")
                newPos = Parameter("pos", "tuple<float,float>")
                newPos.setAttributes(value = f"({source.multi.multiL.value}, {source.multi.multiB.value})", free = source.spatialModel.pos.free)
                source.spatialModel.pos = newPos

                if oldPos != newPos.get():
                    oldDistance = source.spatialModel.get("dist")
                    newDistance = self.getSourceDistance(source)
                    source.spatialModel.dist.setAttributes(value = newDistance)
                    source.multi.set("multiDist", newDistance)
                    self.logger.info(self, f"'pos' parameter has been updated {oldPos}==>{source.spatialModel.get('pos')}")
                    self.logger.info(self, f"'dist' has been updated {oldDistance}==>{source.spatialModel.get('dist')}")
                else:
                    self.logger.info(self, f"'pos' parameter has not changed: {source.spatialModel.get('pos')}")

            else:
                self.logger.info(self, f"multiL,multiB=({source.multi.get('multiL')},{source.multi.get('multiB')}). 'pos' parameter has not changed: {source.spatialModel.get('pos')}")


    def getSourceDistance(self, source):

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

        return AstroUtils.distance(sourceL, sourceB, mapCenterL, mapCenterB)

    def addSource(self, sourceName, sourceObject):

        if not sourceName:
            self.logger.critical(self, "'sourceName' cannot be None or empty.")
            raise SourceParamNotFoundError("'sourceName' cannot be None or empty.")

        for source in self.sources:
            if sourceName == source.name:
                self.logger.warning(self,"The source %s already exists. The 'sourceObject' will not be added to the SourcesLibrary.", sourceName)
                return None

        return SourcesLibrary._addSource(sourceObject, sourceName, self)

    @singledispatch
    def _addSource(sourceObject, sourceName, self):
        raise NotImplementedError('Unsupported type: {}'.format(type(sourceObject)))

    @_addSource.register(Source)
    def _(sourceObject, sourceName, self):

        self.logger.debug(self, "Loading source from a Source object..")

        self.sources.append(sourceObject)

        return sourceObject

    @_addSource.register(dict)
    def _(sourceObject, sourceName, self):

        self.logger.debug(self, "Loading source from a dictionary..")

        requiredKeys = ["glon", "glat", "spectrumType"]

        for rK in requiredKeys:
            if rK not in sourceObject:
                self.logger.critical(self, "'%s' is a required param. Please add it to the 'sourceObject' input dictionary", rK)
                raise SourceParamNotFoundError("'{}' is a required param. Please add it to the 'sourceObject' input dictionary".format(rK))

        newSource = Source(sourceName, "PointSource")

        newSource.spatialModel = SpatialModel.getSpatialModelObject("PointSource", 0)
        newSource.spatialModel.set("pos", f'({sourceObject["glon"]}, {sourceObject["glat"]})')

        newSource.spectrum = Spectrum.getSpectrumObject(sourceObject["spectrumType"])

        spectrumKeys = ["flux", "index", "index1", "index2", "cutoffEnergy", "pivotEnergy", "curvature"]

        for sK in spectrumKeys:
            if sK in vars(newSource.spectrum):
                getattr(newSource.spectrum, sK).set(0)
            if sK in sourceObject and sK in vars(newSource.spectrum):
                getattr(newSource.spectrum, sK).set(sourceObject[sK])

        distance = self.getSourceDistance(newSource)

        newSource.spatialModel.set("dist", distance)

        self.sources.append(newSource)

        return newSource






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
                    SourcesLibrary._fail("Tag <spectrum> or <spatialModel> expected, %s found."%(sourceDescription.tag))

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
                 locationLimit = int(float(elements[7]))
                 spectrumType = int(elements[8])


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

                 if spectrumType == 0:
                     sourceDC.spectrum = Spectrum.getSpectrumObject("PowerLaw")
                 elif spectrumType == 1:
                     sourceDC.spectrum = Spectrum.getSpectrumObject("PLExpCutoff")
                 elif spectrumType == 2:
                     sourceDC.spectrum = Spectrum.getSpectrumObject("PLSuperExpCutoff")
                 elif spectrumType == 3:
                     sourceDC.spectrum = Spectrum.getSpectrumObject("LogParabola")
                 else:
                     self.logger.critical(self,"spectrumType=%d not supported. Supported: [0,1,2,3]", spectrumType)
                     raise SourcesAgileFormatParsingError("spectrumType={} not supported. Supported: [0,1,2,3]".format(spectrumType))


                 getattr(sourceDC.spectrum, "flux").setAttributes(name="flux", free=free_bits[0], value=flux)

                 if spectrumType == 0:
                     getattr(sourceDC.spectrum, "index").setAttributes(name="index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))


                 elif spectrumType == 1:
                     getattr(sourceDC.spectrum, "index").setAttributes(name="index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))

                     getattr(sourceDC.spectrum, "cutoffEnergy").setAttributes(name="cutoffEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14]))

                 elif spectrumType == 2:
                     getattr(sourceDC.spectrum, "index1").setAttributes(name="index1", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))

                     getattr(sourceDC.spectrum, "cutoffEnergy").setAttributes(name="cutoffEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14]))

                     getattr(sourceDC.spectrum, "index2").setAttributes(name="index2", free=free_bits[4], value=float(elements[10]), \
                                                                        min=float(elements[15]), max=float(elements[16]))

                 elif spectrumType == 3:
                     getattr(sourceDC.spectrum, "index").setAttributes(name="index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))

                     getattr(sourceDC.spectrum, "pivotEnergy").setAttributes(name="pivotEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14]))

                     getattr(sourceDC.spectrum, "curvature").setAttributes(name="curvature", free=free_bits[4], value=float(elements[10]), \
                                                                        min=float(elements[15]), max=float(elements[16]))


                 sourceDC.spatialModel = SpatialModel.getSpatialModelObject("PointSource", locationLimit)

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

    def _convertToAgileFormat(self, sources):

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
                sourceStr += "20 10000 0 100"

            elif source.spectrum.stype == "PLExpCutoff":
                sourceStr += str(source.spectrum.cutoffEnergy.min) +" " \
                           + str(source.spectrum.cutoffEnergy.max) +" "\
                           + " 0 100"

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

    def _convertToXmlFormat(self, sources):
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
                                                          "locationLimit": str(source.spatialModel.locationLimit) })

            for parameterDict in source.spatialModel.getParameterDict():

                param_tag = Element("parameter", parameterDict)
                spatial_model_tag.append(param_tag)

            source_tag.append(spatial_model_tag)


        rough_string = tostring(root, 'utf-8')

        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent="  ")


    def _convertToRegFormat(self, sources):
        sourceStr = "galactic\n"

        for source in sources:

            if source.multi == None:
                self.logger.warning(self, f"Multi attribute is None for {source.name}, skipping source..")
                continue

            L = source.multi.get("multiL") 
            B = source.multi.get("multiB") 
            a = source.multi.get("multia") 
            b = source.multi.get("multib") 
            phi = source.multi.get("multiphi")

            if L == -1 and B == -1 and a == -1 and b == -1 and phi == -1:   
                self.logger.info(self, f"L=B=a=b=phi={L} for {source.name}, using LPeak and BPeak..")
                LPeak = source.multi.get("multiLPeak")
                BPeak = source.multi.get("multiBPeak")
                sourceStr += f"ellipse({LPeak}, {BPeak}, 0.5, 0.5, 0) #color=green width=2 text={source.name}"            
            else:
                sourceStr += f"ellipse({L}, {B}, {a}, {b}, {phi}) #color=green width=2 text={source.name}"


            sourceStr += "\n"
        
        return sourceStr

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

    def _addSourcesGenerator(self, sources):
        for source in sources:
            added = self.addSource(source.name, source)
            if added:
                yield added

    def _filterByDistance(self, sources, rangeDist):
        for source in sources:
            distance = self.getSourceDistance(source)
            if distance >= rangeDist[0] and distance <= rangeDist[1]:
                source.spatialModel.set("dist", distance)
                yield source

    def _scaleSourcesFlux(self, sources):

        cat2Emin, cat2Emax = Parameters.getCat2EminEmax()
        uEmin = self.config.getOptionValue("emin")
        uEmax = self.config.getOptionValue("emax")

        for source in sources:

            si = source.getSpectralIndex()

            fl = source.getFlux()

            c = cat2Emin
            d = cat2Emax
            a = uEmin
            b = uEmax

            p1 = fl * (si-1) / ( c ** (1-si) - d ** (1-si) )

            f1 = (p1 / (si-1)) * ( a ** (1-si) - b ** (1-si) )

            source.setFlux(f1)

            yield source
