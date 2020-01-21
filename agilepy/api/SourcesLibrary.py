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

from inspect import signature
from os.path import split, join
import xml.etree.ElementTree as ET
from functools import singledispatch

from agilepy.utils.BooleanExpressionParser import BooleanParser
from agilepy.utils.Utils import agilepyLogger, Astro, Decorators
from agilepy.utils.SourceModel import Source, MultiOutput, Spectrum, SpatialModel, Parameter
from agilepy.utils.CustomExceptions import SourceModelFormatNotSupported, \
                                           FileSourceParsingError, \
                                           SourceNotFound, \
                                           SelectionParamNotSupported

class SourcesLibrary:

    """

        Public Interface

    """


    def __init__(self):
        """
        This method ... blabla ...
        """
        self.logger = agilepyLogger
        self.xmlFilePath = None
        self.xmlFilePathPrefix = None
        self.sources = None


    def loadSourceLibraryXML(self, xmlFilePath):
        """
        This method ... blabla ...
        """
        self.xmlFilePath = xmlFilePath
        self.xmlFilePathPrefix,_ = split(self.xmlFilePath)

        self.sources = self._parseSourceXml(self.xmlFilePath)

        if not self.sources:
            self.logger.warning(self, "Errors during %s parsing", [self.xmlFilePath])
            return False
        else:
            return True


    def writeToFile(self, outfileNamePrefix, format="AG"):
        """
        This method ... blabla ...
        """
        if format not in ["AG"]:#, "XML"]:
            raise SourceModelFormatNotSupported("Format {} not supported. Supported formats: AG".format(format))

        outfilepath = join(self.xmlFilePathPrefix, outfileNamePrefix)

        if format == "AG":

            sourcesAgileFormat = self._convertToAgileFormat()

            outfilepath += ".txt"
            with open(outfilepath, "w") as sourceLibraryFile:

                sourceLibraryFile.write(sourcesAgileFormat)

        else:
            pass
            #outfilepath += ".xml"
            #with open(outfilepath, "w") as sourceLibraryFile:
            #    sourceLibraryFile.write(self.sourcesXML)

        return outfilepath


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
        selectionParamsNames = SourcesLibrary._extractSelectionParams(selection)

        self._checkSelectionParams(selectionParamsNames)

        sources = self._getCompatibleSources(selectionParamsNames)

        selected = []

        for source in sources:

            if self._selectSource(selection, source, selectionParamsNames):

                selected.append(source)

        return selected







    def freeSources(self, selection, parameterName, free):
        """
        Returns the list of sources matching the selection
        """
        sources = self.selectSources(selection)

        if len(sources) == 0:
            self.logger.warning(self, "No sources have been selected.")
            return []

        if parameterName not in self._getFreeParams():
            self.logger.warning(self, 'The parameter %s cannot be released! You can set "free" to: %s', [selectionParam, self._getFreeParams(tostr=True)])
            return []

        return self._setFree(sources, parameterName, free)


    def deleteSources(self, selection):
        """
        This method ... blabla ...

        returns: the list of the deleted sources
        """
        sourcesToBeDeleted = self.selectSources(selection)

        self.sources = [s for s in self.getSources() if s not in sourcesToBeDeleted]

        return sourcesToBeDeleted



    def parseSourceFile(self, sourceFilePath):
        """
        This method ... blabla ...

        returns: a MultiOutput object
        """        # self.logger.info(self, "Parsing output file of AG_multi: %s", [self.outfilePath])

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

        #print("allValues: ", allValues)
        #print("allValues sum: ", len(allValues))

        return MultiOutput(*allValues)



    def updateMulti(self, data, mapCenterL, mapCenterB):

        sourcesFound = self.selectSources(lambda Name : Name == data.label)

        if len(sourcesFound) == 0:
            raise SourceNotFound("Source '%s' has not been found in the sources library"%(data.label))

        for sourceFound in sourcesFound:

            sourceFound.multi = data

            # Computing the distances from maps centers
            # Longitude
            sourceL = float(sourceFound.spatialModel.getParamAttributeWhere("value", "name", "GLON"))
            # Latitude
            sourceB = float(sourceFound.spatialModel.getParamAttributeWhere("value", "name", "GLAT"))

            sourceL = float(data.L)
            sourceB = float(data.B)

            if sourceL == -1:
                sourceL = float(data.start_l)
            if sourceB == -1:
                sourceB = float(data.start_b)


            sourceFound.multi.Dist = Astro.distance(sourceL, sourceB, mapCenterL, mapCenterB)

            self.logger.info(self, "Source '%s' has been updated with 'AG_multi' analysis output", [data.label])








    """

        Private methods

    """
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

            paramsOk = True

            for paramName in validatedUserSelectionParams:

                if paramName in self._getSelectionParams(onlyMultiParams=True) and not source.multi:

                    self.logger.warning(self, "The parameter %s cannot be evaluated on source %s because \
                                               the mle() analysis has not been performed yet on that source.", \
                                               [paramName, source.name])

                    paramsOk = False

            if paramsOk:

                sources.append(source)

        return sources



    def _selectSource(self, selection, source, selectionParamsNames):

        selectionParamsValues = []

        for paramName in selectionParamsNames:

            if paramName == "Name":
                paramValue = getattr(source, "name")
            else:
                paramValue = float(getattr(source.multi, paramName))

            selectionParamsValues.append(paramValue)

        return SourcesLibrary.__selectSource(selection, source, selectionParamsNames, selectionParamsValues)

    @singledispatch
    def __selectSource(selection, source, selectionParamsNames, selectionParamsValues):
        raise NotImplementedError('Unsupported type: {}'.format(type(selection)))

    @__selectSource.register(str)
    def _(selectionStr, source, selectionParamsNames, selectionParamsValues):
        bp = BooleanParser(selectionStr)
        variable_dict = dict(zip(selectionParamsNames, selectionParamsValues))
        return bp.evaluate(variable_dict)

    @__selectSource.register(object)
    def _(selectionLambda, source, selectionParamsNames, selectionParamsValues):
        return selectionLambda(*selectionParamsValues)




    def _setFree(self, sources, parameterName, free):

        for s in sources:

            s.setFreeAttributeValueOf(parameterName, free)

        return sources



    def _checkSelectionParams(self, userSelectionParams):
        """
        Raise exception if at least one param is not supported
        """
        selectionParams = self._getSelectionParams()

        notSupported = []

        for up in userSelectionParams:

            if up not in selectionParams:

                self.logger.critical(self, "The selectionParam %s is not supported and it is not going to be used! \
                                            Supported params: %s", [up, self._getSelectionParams(tostr=True)])

                notSupported.append(up)

        if len(notSupported) > 0:

            raise SelectionParamNotSupported("The following selection params are not supported: {}".format(' '.join(notSupported)))


    def _parseSourceXml(self, xmlFilePath):

        self.logger.info(self, "Parsing %s ...", [xmlFilePath])

        xmlRoot = ET.parse(xmlFilePath).getroot()

        sources = []

        for source in xmlRoot:

            if source.tag != "source":
                self._fail("Tag <source> expected, %s found."%(source.tag))

            sourceDC = Source(**source.attrib)

            for sourceDescription in source:

                if sourceDescription.tag not in ["spectrum", "spatialModel"]:
                    self._fail("Tag <spectrum> or <spatialModel> expected, %s found."%(sourceDescr.tag))

                if sourceDescription.tag == "spectrum":
                    sourceDescrDC = Spectrum(**sourceDescription.attrib, parameters=[])
                    sourceDescrDC = self._checkAndAddParameters(sourceDescrDC, sourceDescription)
                    sourceDC.spectrum = sourceDescrDC
                else:
                    sourceDescrDC = SpatialModel(**sourceDescription.attrib, parameters=[])
                    sourceDescrDC = self._checkAndAddParameters(sourceDescrDC, sourceDescription)
                    sourceDC.spatialModel = sourceDescrDC


            sources.append(sourceDC)

        return sources


    def _checkAndAddParameters(self, sourceDescrDC, sourceDescription):
        for parameter in sourceDescription:

            if parameter.tag != "parameter":
                self._fail("Tag <parameter> expected, %s found."%(parameter.tag))

            paramDC = Parameter(**parameter.attrib)

            sourceDescrDC.parameters.append(paramDC)

        return sourceDescrDC


    def _getConf(self, key=None):
        if not key:
            return self.sources
        else: return self.sources[key]


    def _fail(self, msg):
        raise FileSourceParsingError("File source parsing failed: {}".format(msg))


    def _convertToAgileFormat(self):

        sourceStr = ""

        for source in self.sources:

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

            sourceStr += self._computeFixFlag(source)+" "

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
                sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "Index1") + " " + \
                             source.spectrum.getParamAttributeWhere("max", "name", "Index1") + " "
            else:
                sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "Index") + " " + \
                             source.spectrum.getParamAttributeWhere("max", "name", "Index") + " "


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

        # self.logger.info("Sources configuration in AGILE format placed at: %s", outfilepath)
        return sourceStr


    def _computeFixFlag(self, source):
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


    def _convertToXML(self):
        pass

    def _getSelectionParams(self, tostr = False, onlyMultiParams = False):
        sp = ["Name","Dist", "Flux", "SqrtTS"]
        if onlyMultiParams:
            sp = ["Dist", "Flux", "SqrtTS"]
        if not tostr:
            return sp
        else:
            return ' '.join(sp)

    def _getFreeParams(self, tostr = False):
        fp = ["Flux", "Index", "Index1", "Index2", "CutoffEnergy", "PivotEnergy", "Curvature", "Index2", "Loc"]
        if not tostr:
            return fp
        else:
            return ' '.join(fp)
