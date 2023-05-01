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

import numpy as np
from pathlib import Path
from inspect import signature
from os.path import splitext
from os import listdir
from copy import deepcopy
from datetime import datetime

from functools import singledispatch
from xml.etree.ElementTree import parse, Element, SubElement, Comment, tostring
from xml.dom import minidom

from agilepy.core.Parameters import Parameters
from agilepy.core.source.Source import Source as SourceR
from agilepy.core.source.MultiAnalysis import MultiAnalysis

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

    def searchCatalog(self, catalogName):
        catPath = Utils._expandEnvVar(f"$AGILE/catalogs/{catalogName}.xml")
        if not Path(catPath).exists():
            catPath = Utils._expandEnvVar(f"$AGILE/catalogs/{catalogName}.multi")
            if not Path(catPath).exists():
                self.logger.critical( f"The 2AGL catalog is not available. Please check the $AGILE environment variable.")
                raise FileNotFoundError(f"The 2AGL catalog is not available. Please check the $AGILE environment variable.")
        return catPath

    def loadSourcesFromCatalog(self, catalogName, rangeDist=(0, float("inf")), show=False):
        """
        Load sources from a catalog. For now it supports only the 2AGL catalog.
        TODO: support custom catalogs. In this scenario the user should provide 
        the emin_sources and emax_sources values as input args.
        """
        supportedCatalogs = ["2AGL"]
        
        if catalogName not in supportedCatalogs:
            self.logger.critical( f"The catalog {catalogName} is not supported. Supported catalogs: {supportedCatalogs}")
            raise FileNotFoundError(f"The catalog {catalogName} is not supported. Supported catalogs: {supportedCatalogs}")

        catPath = self.searchCatalog(catalogName)

        catEmin, catEmax = Parameters.getCatEminEmax(catalogName)
        uEmin = np.matrix(self.config.getOptionValue("energybins")).min()
        uEmax = np.matrix(self.config.getOptionValue("energybins")).max()
        scaleFlux = False
        if catEmin != uEmin or catEmax != uEmax:
            scaleFlux = True
            self.logger.warning( f"The input energy range ({uEmin},{uEmax}) is different to the CAT2 energy range ({catEmin},{catEmax}). A scaling of the sources flux will be performed.")

        return self.loadSourcesFromFile(catPath, rangeDist, scaleFlux=scaleFlux, catEmin=catEmin, catEmax=catEmax, show=show)

    def loadSourcesFromFile(self, filePath, rangeDist=(0, float("inf")), scaleFlux=False, catEmin=None, catEmax=None, show=False):

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
            self.logger.critical( "Errors during %s parsing (%s)", filePath, fileExtension)
            raise SourcesFileLoadingError("Errors during {} parsing ({})".format(filePath, fileExtension))

        mapCenterL = float(self.config.getOptionValue("glon"))
        mapCenterB = float(self.config.getOptionValue("glat"))

        for newSource in newSources: newSource.setDistanceFromMapCenter(mapCenterL, mapCenterB)

        filteredSources = [source for source in self._filterByDistance(newSources, rangeDist)]

        filteredSources = [source for source in self._discardIfAlreadyExist(filteredSources)]

        uEmin = np.matrix(self.config.getOptionValue("energybins")).min()
        uEmax = np.matrix(self.config.getOptionValue("energybins")).max()

        if scaleFlux:
            if catEmax is None or catEmin is None:
                raise ValueError("catEmax and catEmin must be provided if scaleFlux is True.")
            scaledSources = []
            for source in filteredSources:
                scaledSources.append(self._scaleSourcesFlux(source, uEmin, uEmax, catEmin, catEmax))
            filteredSources = scaledSources


        if show:
            for s in filteredSources:
                print(f"{s}")

        for source in filteredSources:

            self.sources.append(source)

        self.logger.info( f"Loaded {len(filteredSources)} sources. Total sources: {len(self.sources)}")

        return filteredSources

    def convertCatalogToXml(self, catalogFilepath):

        catalogFilepath = Utils._expandEnvVar(catalogFilepath)

        filename, fileExtension = splitext(catalogFilepath)

        supportedFormats = [".multi", ".txt"]
        if fileExtension not in supportedFormats:
            raise SourceModelFormatNotSupported("Format of {} not supported. Supported formats: {}".format(catalogFilepath, ' '.join(supportedFormats)))

        newSources = self._loadFromSourcesTxt(catalogFilepath)

        return self.writeToFile(filename, fileformat="xml", sources=newSources)

    def writeToFile(self, outfileNamePrefix, fileformat="txt", sources=None, position="ellipse"):

        if fileformat not in ["txt", "xml", "reg"]:
            raise SourceModelFormatNotSupported("Format {} not supported. Supported formats: txt, xml, reg".format(format))

        outputFilePath = self.outdirPath.joinpath(outfileNamePrefix)

        if sources is None:
            sources = self.sources

        if len(sources) == 0:
            self.logger.info("No sources have been loaded yet. No file has been produced.")
            return ""

        if fileformat == "txt":
            sourceLibraryToWrite = self._convertToAgileFormat(sources, position=position)
            outputFilePath = outputFilePath.with_suffix('.txt')

        elif fileformat == "xml":
            sourceLibraryToWrite = self._convertToXmlFormat(sources)
            outputFilePath = outputFilePath.with_suffix('.xml')

        elif fileformat == "reg":
            sourceLibraryToWrite = self._convertToRegFormat(sources)
            outputFilePath = outputFilePath.with_suffix('.reg')

        with open(outputFilePath, "w") as sourceLibraryFile:

            sourceLibraryFile.write(sourceLibraryToWrite)

        self.logger.info("File %s has been produced", outputFilePath)

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

        userSelectionParamsNames = SourcesLibrary._extractSelectionParams(selection)

        selected = []

        for source in self.sources:

            if self._selectSource(selection, source, userSelectionParamsNames):

                selected.append(source)

        if show:
            for s in selected:
                print(f"{s}")

        return selected

    def fixSource(self, source):
        """
        Set to False all freeable params of a source
        """
        affected = False

        freeableParams = source.getFreeableParams()

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

        affected = []

        for s in sources:

            if s.setFreeAttributeValueOf(parameterName, free):

                affected.append(s)

                if show:
                    print(f"{s}")
                    # self.logger.info( f"{s}")

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
                # self.logger.info( f"{s}")

        self.logger.info( "Deleted %d sources.", len(deletedSources))
        return deletedSources

    def parseSourceFile(self, sourceFilePath):
        """
        Static method

        returns: a MultiAnalysis object
        """
        self.logger.debug(f"Parsing output file of AG_multi: {sourceFilePath}")

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
            self.logger.critical(f"The values extracted from {sourceFilePath} file are lesser then 128")
            raise FileSourceParsingError("The values extracted from {} file are lesser then 128".format(sourceFilePath))

        multiAnalysisResult = MultiAnalysis()

        multiAnalysisResult.setParameter("multiDate", {"value": datetime.now()})

        multiAnalysisResult.setParameter("multiName", {"value": allValues[0]})

        multiAnalysisResult.setParameter("multiFix", {"value": allValues[1]})
        multiAnalysisResult.setParameter("multiindex", {"value": allValues[2]})
        multiAnalysisResult.setParameter("multiULConfidenceLevel", {"value": allValues[3]})
        multiAnalysisResult.setParameter("multiSrcLocConfLevel", {"value": allValues[4]})

        multiAnalysisResult.setParameter("multiStartL", {"value": allValues[5]})
        multiAnalysisResult.setParameter("multiStartB", {"value": allValues[6]})

        multiAnalysisResult.setParameter("multiStartFlux", {"value": allValues[7]})
        multiAnalysisResult.setParameter("multiTypefun", {"value": allValues[12]})
        multiAnalysisResult.setParameter("multipar2", {"value": allValues[13]})
        multiAnalysisResult.setParameter("multipar3", {"value": allValues[14]})
        multiAnalysisResult.setParameter("multiGalmode2", {"value": allValues[15]})
        multiAnalysisResult.setParameter("multiGalmode2fit", {"value": allValues[16]})
        multiAnalysisResult.setParameter("multiIsomode2", {"value": allValues[17]})
        multiAnalysisResult.setParameter("multiIsomode2fit", {"value": allValues[18]})
        multiAnalysisResult.setParameter("multiEdpcor", {"value": allValues[19]})
        multiAnalysisResult.setParameter("multiFluxcor", {"value": allValues[20]})
        multiAnalysisResult.setParameter("multiIntegratorType", {"value": allValues[21]})
        multiAnalysisResult.setParameter("multiExpratioEval", {"value": allValues[22]})
        multiAnalysisResult.setParameter("multiExpratioMinthr", {"value": allValues[23]})
        multiAnalysisResult.setParameter("multiExpratioMaxthr", {"value": allValues[24]})
        multiAnalysisResult.setParameter("multiExpratioSize", {"value": allValues[25]})
    

        multiAnalysisResult.setParameter("multiSqrtTS", {"value": allValues[37]})

        multiAnalysisResult.setParameter("multiFlux", {"value": allValues[53]})
        multiAnalysisResult.setParameter("multiFluxErr", {"value": allValues[54]})
        multiAnalysisResult.setParameter("multiFluxPosErr", {"value": allValues[55]})
        multiAnalysisResult.setParameter("multiFluxNegErr", {"value": allValues[56]})

        multiAnalysisResult.setParameter("multiUL", {"value": allValues[57]})

        multiAnalysisResult.setParameter("multiExp", {"value": allValues[59]})


        multiAnalysisResult.setParameter("multiErgLog", {"value": allValues[64]})
        multiAnalysisResult.setParameter("multiErgLogErr", {"value": allValues[65]})
        multiAnalysisResult.setParameter("multiErgLogUL", {"value": allValues[66]})

        multiAnalysisResult.setParameter("multiLPeak", {"value": allValues[38]})
        multiAnalysisResult.setParameter("multiBPeak", {"value": allValues[39]})
        multiAnalysisResult.setParameter("multiDistFromStartPositionPeak", {"value": allValues[40]})

        multiAnalysisResult.setParameter("multiL", {"value": allValues[41]})
        multiAnalysisResult.setParameter("multiB", {"value": allValues[42]})
        multiAnalysisResult.setParameter("multiDistFromStartPosition", {"value": allValues[43]})
        multiAnalysisResult.setParameter("multir", {"value": allValues[44]})
        multiAnalysisResult.setParameter("multia", {"value": allValues[45]})
        multiAnalysisResult.setParameter("multib", {"value": allValues[46]})
        multiAnalysisResult.setParameter("multiphi", {"value": allValues[47]})

        multiAnalysisResult.setParameter("multiCounts", {"value": allValues[48]})
        multiAnalysisResult.setParameter("multiCountsErr", {"value": allValues[49]})


        multiAnalysisResult.setParameter("multiIndex", {"value": allValues[69]})
        multiAnalysisResult.setParameter("multiIndexErr", {"value": allValues[70]})
        
        multiAnalysisResult.setParameter("multiPar2", {"value": allValues[71]})
        multiAnalysisResult.setParameter("multiPar2Err", {"value": allValues[72]})

        multiAnalysisResult.setParameter("multiPar3", {"value": allValues[73]})
        multiAnalysisResult.setParameter("multiPar3Err", {"value": allValues[74]})

        multiAnalysisResult.setParameter("multiFitCts", {"value": allValues[75]})
        multiAnalysisResult.setParameter("multiFitFitstatus0", {"value": allValues[76]})
        multiAnalysisResult.setParameter("multiFitFcn0", {"value":  allValues[77]})
        multiAnalysisResult.setParameter("multiFitEdm0", {"value": allValues[78]})
        multiAnalysisResult.setParameter("multiFitNvpar0", {"value": allValues[79]})
        multiAnalysisResult.setParameter("multiFitNparx0", {"value": allValues[80]})
        multiAnalysisResult.setParameter("multiFitIter0", {"value": allValues[81]})
        multiAnalysisResult.setParameter("multiFitFitstatus1", {"value": allValues[82]})
        multiAnalysisResult.setParameter("multiFitFcn1", {"value": allValues[83]})
        multiAnalysisResult.setParameter("multiFitEdm1", {"value": allValues[84]})
        multiAnalysisResult.setParameter("multiFitNvpar1", {"value": allValues[85]})
        multiAnalysisResult.setParameter("multiFitNparx1", {"value": allValues[86]})
        multiAnalysisResult.setParameter("multiFitIter1", {"value": allValues[87]})
        multiAnalysisResult.setParameter("multiFitLikelihood1", {"value": allValues[88]})

        multiAnalysisResult.setParameter("multiGalCoeff", {"value": [eval(val) for val in allValues[89]]})
        multiAnalysisResult.setParameter("multiGalErr", {"value": [eval(val) for val in allValues[90]]})
        multiAnalysisResult.setParameter("multiIsoCoeff", {"value": [eval(val) for val in allValues[93]]})
        multiAnalysisResult.setParameter("multiIsoErr", {"value": [eval(val) for val in allValues[94]]})

        multiAnalysisResult.setParameter("startDataTT", {"value": allValues[99]})
        multiAnalysisResult.setParameter("endDataTT", {"value": allValues[100]})


        multiAnalysisResult.setParameter("multiEmin", {"value": allValues[103]})
        multiAnalysisResult.setParameter("multiEmax", {"value": allValues[104]})
        multiAnalysisResult.setParameter("multifovmin", {"value": allValues[105]})
        multiAnalysisResult.setParameter("multifovmax", {"value": allValues[106]})
        multiAnalysisResult.setParameter("multialbedo", {"value": allValues[107]})
        multiAnalysisResult.setParameter("multibinsize", {"value": allValues[108]})
        multiAnalysisResult.setParameter("multiexpstep", {"value": allValues[109]})
        multiAnalysisResult.setParameter("multiphasecode", {"value": allValues[110]})

        multiAnalysisResult.setParameter("multiExpRatio", {"value": allValues[111]})

        return multiAnalysisResult

    def updateSourceWithMLEResults(self, multiAnalysisResult):
        
        sourceName = multiAnalysisResult.get("multiName")["value"]

        sources = self.selectSources(lambda name : name == sourceName, show=False)

        if len(sources) == 0:
            raise SourceNotFound(f"Source '{sourceName}' has not been found in the sources library")
        
        if len(sources) > 1:
            self.logger.warning(self, f"Found more than one source:{sources}")

        mapCenterL = float(self.config.getOptionValue("glon"))
        mapCenterB = float(self.config.getOptionValue("glat"))

        sources.pop().updateMultiAnalysis(multiAnalysisResult, mapCenterL, mapCenterB)

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

        source.set("pos", {"value": (glon, glat)})

        mapCenterL = float(self.config.getOptionValue("glon"))
        mapCenterB = float(self.config.getOptionValue("glat"))
        source.setDistanceFromMapCenter(mapCenterL, mapCenterB)

    def doesSourceAlreadyExist(self, sourceName):
        for source in self.sources:
            if sourceName == source.name:
                return True
        return False

    def addSource(self, sourceName, sourceObject):

        if not sourceName:
            self.logger.critical(f"sourceName='{sourceName}' cannot be None or empty.")
            raise SourceParamNotFoundError(f"sourceName='{sourceName}' cannot be None or empty.")

        if self.doesSourceAlreadyExist(sourceName):
                self.logger.warning(self,"The source %s already exists. The 'sourceObject' will not be added to the SourcesLibrary.", sourceName)
                return None

        return SourcesLibrary._addSource(sourceObject, sourceName, self)

    @singledispatch
    def _addSource(sourceObject, sourceName, self):
        raise NotImplementedError('Unsupported type: {}'.format(type(sourceObject)))

    @_addSource.register(SourceR)
    def _(sourceObject, sourceName, self):

        self.logger.debug( "Loading source from a Source object..")

        self.sources.append(sourceObject)

        return sourceObject

    @_addSource.register(dict)
    def _(sourceDict, sourceName, self):

        self.logger.debug( "Loading source from a dictionary..")

        newSource = SourceR.fromDictionary(sourceName, sourceDict)

        mapCenterL = float(self.config.getOptionValue("glon"))
        mapCenterB = float(self.config.getOptionValue("glat"))
        newSource.setDistanceFromMapCenter(mapCenterL, mapCenterB)

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

    def _selectSource(self, selection, source, userSelectionParams):
        
        selectionParamsValues = []
        
        for paramName in userSelectionParams:
            paramValue = source.getSelectionValue(paramName)
            if paramValue is not None:
                selectionParamsValues.append(paramValue)
            else:
                self.logger.warning(self, f"The selection parameter '{paramName}' cannot be used for source '{source.name}' since mle() has not been called yet! Skipping source..")
                return None

        self.logger.debug( f"userSelectionParams: {userSelectionParams} selectionParamsValues: {selectionParamsValues}")

        return SourcesLibrary.__selectSource(selection, source, userSelectionParams, selectionParamsValues)

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

        self.logger.debug( f"Parsing {xmlFilePath} ...")

        xmlRoot = parse(xmlFilePath).getroot()

        sources = []

        for sourceRoot in xmlRoot:

            source = SourceR.parseSourceXMLFormat(sourceRoot)

            sources.append(source)

        return sources


    def _loadFromSourcesTxt(self, txtFilePath):

        sources = []

        with open(txtFilePath, "r") as txtFile:

            for line in txtFile:

                if line == "\n":
                    continue

                source = SourceR.parseSourceTXTFormat(line)

                sources.append(source)

        return sources


    def _getConf(self, key=None):
        if not key:
            return self.sources
        else: return self.sources[key]

    @staticmethod
    def _fail(msg):
        raise FileSourceParsingError("File source parsing failed: {}".format(msg))

    def _convertToAgileFormat(self, sources, position="ellipse"):

        sourceStr = ""

        for source in sources:

            # get flux value
            if source.get("multiDate")["value"]:
                flux = source.get("multiFlux")["value"]
            else:
                flux = source.get("flux")["value"]

            sourceStr += str(flux)+" "

            # set l and b according to card #335
            #

            """
            Multi parameter mapping
            "flux" : "multiFlux",
            "index" : "multiIndex",
            "index1" : "multiIndex",
            "cutoffEnergy" : "multiPar2",
            "pivotEnergy" : "multiPar2",
            "index2" : "multiPar3",
            "curvature" : "multiPar3",
            """
            
            multiL = source.get("multiL")["value"] 
            multiB = source.get("multiB")["value"] 
            multiLPeak = source.get("multiLPeak")["value"]
            multiBPeak = source.get("multiBPeak")["value"]
            index = source.get("multiIndex")["value"]
            pos = source.get("pos")["value"]
            startL = pos[0]
            startB = pos[1]

            glon = multiL
            glat = multiB

            self.logger.debug(f"Parameters: multiL={multiL}, multiB={multiB}, multiLPeak={multiLPeak}, multiBPeak={multiBPeak}, startL={startL}, startB={startB} ")

            if glon == -1 or glat == -1 or position == "peak" or glon == None or glat == None:
                glon = multiLPeak
                glat = multiBPeak
                self.logger.debug(f"Ellipse values not available, I got peak values")
            
            if glon == -1 or glat == -1 or position == "initial" or glon == None or glat == None:
                glon = startL
                glat = startB
                self.logger.debug(f"Ellipse and peak values not available, I got initial values")
           
            sourceStr += str(glon) + " "
            sourceStr += str(glat) + " "
            
            if index is not None:
                sourceStr += str(index) + " "
            else:
                sourceStr += str(source.spectrum.getSpectralIndex()) + " "

            sourceStr += SourcesLibrary._computeFixFlag(source, source.spectrum.getType())+" "

            sourceStr += "2 "

            sourceStr += source.name + " "

            sourceStr += str(source.get("locationLimit")["value"]) + " "

            if source.spectrum.getType() == "PowerLaw":
                sourceStr += "0 0 0 "

            elif source.spectrum.getType() == "PLExpCutoff":
                cutoffenergy = source.get("multiPar2")["value"] 
                if cutoffenergy is None:
                    cutoffenergy = source.get("cutoffEnergy")["value"]
                sourceStr += "1 "+str(cutoffenergy)+" 0 "

            elif source.spectrum.getType() == "PLSuperExpCutoff":
                
                cutoffenergy = source.get("multiPar2")["value"] 
                if cutoffenergy is None:
                    cutoffenergy = source.get("cutoffEnergy")["value"]
                
                index2 = source.get("multiPar3")["value"]
                if index2 is None:
                    index2 = source.get("index2")["value"]
                
                sourceStr += "2 "+str(cutoffenergy)+" "+str(index2)+" "

            elif source.spectrum.getType() == "LogParabola":
                
                pivotenergy = source.get("multiPar2")["value"] 
                if pivotenergy is None:
                    pivotenergy = source.get("pivotEnergy")["value"]

                curvature = source.get("multiPar3")["value"] 
                if curvature is None:
                    curvature = source.get("curvature")["value"]
                sourceStr += "3 "+str(pivotenergy)+" "+str(curvature)+" "

            else:
                raise ValueError("Spectrum type not supported!")

            # Adding index limit min and max values
            if source.spectrum.getType() == "PLSuperExpCutoff":
                sourceStr += str(source.get("index1")["min"]) + " " + \
                             str(source.get("index1")["max"]) + " "
            else:
                sourceStr += str(source.get("index")["min"]) + " " + \
                             str(source.get("index")["max"]) + " "

            # Adding par2 and par3 limit min and max values
            if source.spectrum.getType() == "PowerLaw":
                sourceStr += "20 10000 0 100"

            elif source.spectrum.getType() == "PLExpCutoff":
                sourceStr += str(source.get("cutoffEnergy")["min"]) +" " \
                           + str(source.get("cutoffEnergy")["max"]) +" "\
                           + " 0 100"

            elif source.spectrum.getType() == "PLSuperExpCutoff":
                sourceStr += str(source.get("cutoffEnergy")["min"]) +" "\
                           + str(source.get("cutoffEnergy")["max"]) +" "\
                           + str(source.get("index2")["min"]) +" "\
                           + str(source.get("index2")["max"])

            else:
                sourceStr += str(source.get("pivotEnergy")["min"]) +" "\
                           + str(source.get("pivotEnergy")["max"]) +" "\
                           + str(source.get("curvature")["min"]) +" "\
                           + str(source.get("curvature")["max"])


            sourceStr += "\n"

        return sourceStr

    def _convertToXmlFormat(self, sources):
        """
        https://pymotw.com/2/xml/etree/ElementTree/create.html
        """
        root = Element('source_library', title="source library")

        for source in sources:

            source_tag = SubElement(root, "source", {"name": source.name, "type": "PointSource"})

            spectrum_tag = Element("spectrum", {"type": source.spectrum.getType()})

            for parameterDict in source.spectrum.getAttributes():
                parameterDict.pop("err", None)
                parameterDict.pop("datatype", None)
                parameterDict.pop("um", None)
                for key,val in parameterDict.items():
                    parameterDict[key] = str(val)
                param_tag = Element("parameter", parameterDict)
                spectrum_tag.append(param_tag)

            source_tag.append(spectrum_tag)

            spatial_model_tag = Element("spatialModel", { "type": source.spatialModel.getType(), \
                                                          "location_limit": str(source.get("locationLimit")["value"]) })

            posParam = source.get("pos")
            posParam.pop("datatype", None)
            posParam.pop("um", None)
            for key,val in posParam.items():
                    posParam[key] = str(val)

            param_tag = Element("parameter", posParam)
            spatial_model_tag.append(param_tag)

            source_tag.append(spatial_model_tag)


        rough_string = tostring(root, 'utf-8')

        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent="  ")


    def _convertToRegFormat(self, sources):
        sourceStr = "galactic\n"

        for source in sources:

            if source.get("multiDate")["value"] is None:
                self.logger.warning(self, f"Multi attribute is None for {source.name}, skipping source..")
                continue

            L = source.get("multiL")["value"] 
            B = source.get("multiB")["value"] 
            a = source.get("multia")["value"] 
            b = source.get("multib")["value"] 
            phi = source.get("multiphi")["value"]

            if L == -1 and B == -1 and a == -1 and b == -1 and phi == -1:   
                self.logger.info( f"L=B=a=b=phi={L} for {source.name}, using LPeak and BPeak..")
                LPeak = source.get("multiLPeak")["value"]
                BPeak = source.get("multiBPeak")["value"]
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

        freeParams = source.getFreeParams()
        
        posFree = "1" if "pos" in freeParams else "0"
        fluxFree = "1" if "flux" in freeParams else "0"
        indexFree = "1" if "index" in freeParams else "0"
        cutoffEnergyFree = "1" if "cutoffEnergy" in freeParams else "0"
        index1Free = "1" if "index1" in freeParams else "0"
        index2Free = "1" if "index2" in freeParams else "0"
        curvatureFree = "1" if "curvature" in freeParams else "0"
        pivotEnergyFree = "1" if "pivotEnergy" in freeParams else "0"

        #if fluxFree == "0":
        #    return "0"

        bit_1 = fluxFree
        
        bit_2 = posFree
        if source.spatialModel.pos["free"] == 2:
            bit_2 = "0"
        
        bit_3 = indexFree
        if spectrumType == "PLSuperExpCutoff":
            bit_3 = index1Free
        
        bit_4 = "0" # PowerLaw
        if spectrumType == "PLExpCutoff":
            bit_4 = cutoffEnergyFree
        elif spectrumType == "PLSuperExpCutoff":
            bit_4 = cutoffEnergyFree
        elif spectrumType == "LogParabola":
            bit_4 = pivotEnergyFree

        bit_5 = "0" # PowerLaw
        if spectrumType == "PLSuperExpCutoff":
            bit_5 = index2Free
        elif spectrumType == "LogParabola":
            bit_5 = curvatureFree

        bit_6 = "0"
        if source.spatialModel.pos["free"] == 2:
            bit_6 = "1"

        # create the bitmask in reverse order
        bitmask = bit_6 + bit_5 + bit_4 + bit_3 + bit_2 + bit_1
        fixflag = int(bitmask, 2)

        return str(fixflag)

    def _discardIfAlreadyExist(self, sources):
        for source in sources:
            if not self.doesSourceAlreadyExist(source.name):
                yield source

    def _filterByDistance(self, sources, rangeDist):
        for source in sources:
            distance = source.get("dist")["value"]
            if distance >= rangeDist[0] and distance <= rangeDist[1]:
                yield source

    def _scaleSourcesFlux(self, source, emin, emax, catEmin, catEmax):

        si = source.spectrum.getSpectralIndex()
        fl = source.spectrum.getVal("flux")
        c = catEmin
        d = catEmax
        a = emin
        b = emax

        p1 = fl * (si-1) / ( c ** (1-si) - d ** (1-si) )
        f1 = (p1 / (si-1)) * ( a ** (1-si) - b ** (1-si) )
        source.set("flux", {"value": f1})

        return source
