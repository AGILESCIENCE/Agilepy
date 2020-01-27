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
from functools import singledispatch
from xml.etree.ElementTree import parse
#from ElementTree_pretty import prettify
#from xml.etree.ElementTree import parse, Element, SubElement, Comment

from agilepy.utils.Utils import agilepyLogger, Astro
from agilepy.utils.BooleanExpressionParser import BooleanParser
from agilepy.utils.SourceModel import Source, MultiOutput, Spectrum, SpatialModel, Parameter
from agilepy.utils.CustomExceptions import SourceModelFormatNotSupported, \
                                           FileSourceParsingError, \
                                           SourceNotFound, \
                                           SelectionParamNotSupported, \
                                           SourcesFileLoadingError, \
                                           SourcesAgileFormatParsingError

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


    def loadSources(self, filePath, fileformat="XML"):
        """
        This method ... blabla ...
        """
        if fileformat not in ["AG", "XML"]:
            raise SourceModelFormatNotSupported("Format {} not supported. Supported formats: AG, XML".format(format))

        self.sourcesFilePathFormat = format
        self.sourcesFilePath = filePath
        self.sourcesFilePathPrefix,_ = split(self.sourcesFilePath)

        if fileformat == "XML":
            self.sources = self._loadFromSourcesXml(self.sourcesFilePath)

        else:
            self.sources = self._loadFromSourcesTxt(self.sourcesFilePath)

        if not self.sources:

            self.logger.critical(self, "Errors during %s parsing (format %s)", [self.sourcesFilePath, self.sourcesFilePathFormat])
            raise SourcesFileLoadingError("Errors during {} parsing (format {})".format(self.sourcesFilePath, self.sourcesFilePathFormat))

        else:
            return True




    def writeToFile(self, outfileNamePrefix, fileformat="AG"):
        """
        This method ... blabla ...
        """
        if fileformat not in ["AG", "XML"]:
            raise SourceModelFormatNotSupported("Format {} not supported. Supported formats: AG, XML".format(format))

        outfilepath = join(self.sourcesFilePathPrefix, outfileNamePrefix)

        if fileformat == "AG":
            sourceLibraryToWrite = self._convertToAgileFormat()
            outfilepath += ".txt"

        else:
            sourceLibraryToWrite = SourcesLibrary._convertToXmlFormat()
            outfilepath += ".xml"

        with open(outfilepath, "w") as sourceLibraryFile:

            sourceLibraryFile.write(sourceLibraryToWrite)


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

            if SourcesLibrary._selectSource(selection, source, selectionParamsNames):

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

        if parameterName not in SourcesLibrary._getFreeParams():
            self.logger.warning(self, 'The parameter %s cannot be released! You can set "free" to: %s', \
                                       [selectionParam, SourcesLibrary._getFreeParams(tostr=True)])
            return []

        return SourcesLibrary._setFree(sources, parameterName, free)


    def deleteSources(self, selection):
        """
        This method ... blabla ...

        returns: the list of the deleted sources
        """
        deletedSources = self.selectSources(selection)

        self.sources = [s for s in self.getSources() if s not in deletedSources]

        return deletedSources


    @staticmethod
    def parseSourceFile(sourceFilePath):
        """
        Static method

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

        if len(allValues) != 128:
            self.logger.critical(self, "The values extracted from %s file are lesser then 128", [sourceFilePath])
            raise FileSourceParsingError("The values extracted from {} file are lesser then 128".format(sourceFilePath))
        #print("allValues: ", allValues)
        #print("allValues sum: ", len(allValues))
        multiOutput = MultiOutput(*allValues)
        multiOutput.convertToFloat()

        return multiOutput



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
            self.logger.info(self, "'Dist' parameter of '%s' has been updated: %f", [data.label, float(sourceFound.multi.Dist)])

            if sourceFound.setParamValue("Flux", sourceFound.multi.Flux):

                self.logger.info(self, "'Flux' parameter of '%s' has been updated: %f", [data.label, float(sourceFound.multi.Flux)])

            else:

                self.warning.info(self, "'Flux' parameter of '%s' has been updated: %f", [data.label, float(sourceFound.multi.Flux)])





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

                if paramName in SourcesLibrary._getSelectionParams(onlyMultiParams=True) and not source.multi:

                    self.logger.warning(self, "The parameter %s cannot be evaluated on source %s because \
                                               the mle() analysis has not been performed yet on that source.", \
                                               [paramName, source.name])

                    paramsOk = False

            if paramsOk:

                sources.append(source)

        return sources


    @staticmethod
    def _selectSource(selection, source, selectionParamsNames):

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



    @staticmethod
    def _setFree(sources, parameterName, free):

        for s in sources:

            s.setFreeAttributeValueOf(parameterName, free)

        return sources



    def _checkSelectionParams(self, userSelectionParams):
        """
        Raise exception if at least one param is not supported
        """
        selectionParams = SourcesLibrary._getSelectionParams()

        notSupported = []

        for up in userSelectionParams:

            if up not in selectionParams:

                self.logger.critical(self, "The selectionParam %s is not supported and it is not going to be used! \
                                            Supported params: %s", [up, SourcesLibrary._getSelectionParams(tostr=True)])

                notSupported.append(up)

        if len(notSupported) > 0:

            raise SelectionParamNotSupported("The following selection params are not supported: {}".format(' '.join(notSupported)))


    def _loadFromSourcesXml(self, xmlFilePath):

        self.logger.info(self, "Parsing %s ...", [xmlFilePath])

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
                    sourceDescrDC = Spectrum(sourceDescription.attrib["type"])
                    sourceDescrDC = SourcesLibrary._checkAndAddParameters(sourceDescrDC, sourceDescription)
                    sourceDC.spectrum = sourceDescrDC
                else:
                    sourceDescrDC = SpatialModel(sourceDescription.attrib["type"], sourceDescription.attrib["location_limit"], sourceDescription.attrib["free"])
                    sourceDescrDC = SourcesLibrary._checkAndAddParameters(sourceDescrDC, sourceDescription)
                    sourceDC.spatialModel = sourceDescrDC


            sources.append(sourceDC)

        return sources


    def _loadFromSourcesTxt(self, txtFilePath):

        sources = []

        with open(txtFilePath, "r") as txtFile:

             for line in txtFile:

                 elements = [elem.strip() for elem in line.split(" ") if elem] # each line is a source

                 if len(elements) != 17:
                     self.logger.critical(self, "The number of elements on the line %s is not 17", [line])
                     raise SourcesAgileFormatParsingError("The number of elements on the line {} is not 17".format(line))

                 flux = float(elements[0])
                 glon = float(elements[1])
                 glat = float(elements[2])
                 index = float(elements[3])
                 fixflag = int(elements[4])
                 name = elements[6]
                 location_limit = float(elements[7])
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

                 sourceDC.spectrum = Spectrum(type="")

                 sourceDC.spectrum.parameters.append(Parameter(name="Flux", free=free_bits[0], value=flux))

                 if spectrum_type == 0:
                     sourceDC.spectrum.type = "PowerLaw"
                     sourceDC.spectrum.parameters.append(Parameter(name="Index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12])))

                 elif spectrum_type == 1:
                     sourceDC.spectrum.type = "PLExpCutoff"
                     sourceDC.spectrum.parameters.append(Parameter(name="Index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12])))

                     sourceDC.spectrum.parameters.append(Parameter(name="CutoffEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14])))

                 elif spectrum_type == 2:
                     sourceDC.spectrum.type = "PLSuperExpCutoff"

                     sourceDC.spectrum.parameters.append(Parameter(name="Index1", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12])))

                     sourceDC.spectrum.parameters.append(Parameter(name="CutoffEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14])))

                     sourceDC.spectrum.parameters.append(Parameter(name="Index2", free=free_bits[4], value=float(elements[10]), \
                                                                        min=float(elements[15]), max=float(elements[16])))

                 elif spectrum_type == 3:
                     sourceDC.spectrum.type = "LogParabola"
                     p = Parameter(name="Index", free=free_bits[2], scale=-1.0, \
                                                                        value=index, min=float(elements[11]), max=float(elements[12]))
                                                                        
                     sourceDC.spectrum.parameters.append(p)

                     sourceDC.spectrum.parameters.append(Parameter(name="PivotEnergy", free=free_bits[3], scale=-1.0, \
                                                                        value=float(elements[9]), min=float(elements[13]), max=float(elements[14])))

                     sourceDC.spectrum.parameters.append(Parameter(name="Curvature", free=free_bits[4], value=float(elements[10]), \
                                                                        min=float(elements[15]), max=float(elements[16])))


                 else:
                     self.logger.critical(self,"spectrum_type=%d not supported. Supported: [0,1,2,3]", [spectrum_type])
                     raise SourcesAgileFormatParsingError("spectrum_type={} not supported. Supported: [0,1,2,3]".format(spectrum_type))

                 sourceDC.spatialModel = SpatialModel(type="PointSource", location_limit=location_limit, free=free_bits_position)
                 sourceDC.spatialModel.parameters.append(Parameter(name="GLON", value=glon))
                 sourceDC.spatialModel.parameters.append(Parameter(name="GLAT", value=glat))


                 sources.append(sourceDC)

        return sources


    @staticmethod
    def _checkAndAddParameters(sourceDescrDC, sourceDescription):
        for parameter in sourceDescription:

            if parameter.tag != "parameter":
                SourcesLibrary._fail("Tag <parameter> expected, %s found."%(parameter.tag))

            paramDC = Parameter(**parameter.attrib)
            sourceDescrDC.parameters.append(paramDC)

        return sourceDescrDC


    def _getConf(self, key=None):
        if not key:
            return self.sources
        else: return self.sources[key]


    @staticmethod
    def _fail(msg):
        raise FileSourceParsingError("File source parsing failed: {}".format(msg))


    def _convertToAgileFormat(self):

        sourceStr = ""

        for source in self.sources:

            # get flux value
            flux = source.getParamValue("Flux")
            sourceStr += str(flux)+" "

            # glon e glat
            glon = source.spatialModel.getParamAttributeWhere("value", "name", "GLON")
            glat = source.spatialModel.getParamAttributeWhere("value", "name", "GLAT")
            sourceStr += str(glon) + " "
            sourceStr += str(glat) + " "


            if source.spectrum.type == "PLSuperExpCutoff":
                index1 = source.spectrum.getParamAttributeWhere("value", "name", "Index1")
                sourceStr += str(index1) + " "
            else:
                index = source.spectrum.getParamAttributeWhere("value", "name", "Index")
                sourceStr += str(index) + " "

            sourceStr += SourcesLibrary._computeFixFlag(source)+" "

            sourceStr += "2 "

            sourceStr += source.name + " "

            sourceStr += str(source.spatialModel.location_limit) + " "


            if source.spectrum.type == "PowerLaw":
                sourceStr += "0 0 0 "

            elif source.spectrum.type == "PLExpCutoff":
                cutoffenergy = source.spectrum.getParamAttributeWhere("value", "name", "CutoffEnergy", strRepr=True)
                sourceStr += "1 "+str(cutoffenergy)+" 0 "

            elif source.spectrum.type == "PLSuperExpCutoff":
                cutoffenergy = source.spectrum.getParamAttributeWhere("value", "name", "CutoffEnergy", strRepr=True)
                index2 = source.spectrum.getParamAttributeWhere("value", "name", "Index2", strRepr=True)
                sourceStr += "2 "+str(cutoffenergy)+" "+str(index2)+" "

            else:
                pivotenergy = source.spectrum.getParamAttributeWhere("value", "name", "PivotEnergy", strRepr=True)
                curvature = source.spectrum.getParamAttributeWhere("value", "name", "Curvature", strRepr=True)
                sourceStr += "3 "+str(pivotenergy)+" "+str(curvature)+" "



            if source.spectrum.type == "PLSuperExpCutoff":
                sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "Index1", strRepr=True) + " " + \
                             source.spectrum.getParamAttributeWhere("max", "name", "Index1", strRepr=True) + " "
            else:
                sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "Index", strRepr=True) + " " + \
                             source.spectrum.getParamAttributeWhere("max", "name", "Index", strRepr=True) + " "


            if source.spectrum.type == "PowerLaw":
                sourceStr += "-1 -1 -1 -1"

            elif source.spectrum.type == "PLExpCutoff":
                sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "CutoffEnergy", strRepr=True) +" "\
                           + source.spectrum.getParamAttributeWhere("max", "name", "CutoffEnergy", strRepr=True) +" "\
                           + " -1 -1"

            elif source.spectrum.type == "PLSuperExpCutoff":
                sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "CutoffEnergy", strRepr=True) +" "\
                           + source.spectrum.getParamAttributeWhere("max", "name", "CutoffEnergy", strRepr=True) +" "\
                           + source.spectrum.getParamAttributeWhere("min", "name", "Index2", strRepr=True) +" "\
                           + source.spectrum.getParamAttributeWhere("max", "name", "Index2", strRepr=True)

            else:
                sourceStr += source.spectrum.getParamAttributeWhere("min", "name", "PivotEnergy", strRepr=True) +" "\
                           + source.spectrum.getParamAttributeWhere("max", "name", "PivotEnergy", strRepr=True) +" "\
                           + source.spectrum.getParamAttributeWhere("min", "name", "Curvature", strRepr=True) +" "\
                           + source.spectrum.getParamAttributeWhere("max", "name", "Curvature", strRepr=True)


            sourceStr += "\n"

        # self.logger.info("Sources configuration in AGILE format placed at: %s", outfilepath)
        return sourceStr

    @staticmethod
    def _convertToXmlFormat():
        """
        https://pymotw.com/2/xml/etree/ElementTree/create.html
        top = Element('source_library', title="source library")

        doc = SubElement(root, "doc")

        SubElement(doc, "field1", name="blah").text = "some value1"
        SubElement(doc, "field2", name="asdfasd").text = "some vlaue2"

        tree = ET.ElementTree(root)
        tree.write("filename.xml")
        return prettify(top)
        """
        return ""


    @staticmethod
    def _computeFixFlag(source):

        if source.spectrum.getFreeAttributeValueOf("name", "Flux") == 0:
            return "0"

        if source.spatialModel.free == 2:

            bitmask = source.spatialModel.free + \
                      source.spectrum.getFreeAttributeValueOf("name", "Curvature", strRepr=True) + source.spectrum.getFreeAttributeValueOf("name", "Index2", strRepr=True) + \
                      source.spectrum.getFreeAttributeValueOf("name", "CutoffEnergy", strRepr=True) + source.spectrum.getFreeAttributeValueOf("name", "PivotEnergy", strRepr=True) + \
                      source.spectrum.getFreeAttributeValueOf("name", "Index", strRepr=True) + source.spectrum.getFreeAttributeValueOf("name", "Index1", strRepr=True) + \
                      "0" + \
                      source.spectrum.getFreeAttributeValueOf("name", "Flux", strRepr=True)

        else:

            bitmask = source.spectrum.getFreeAttributeValueOf("name", "Curvature", strRepr=True) + source.spectrum.getFreeAttributeValueOf("name", "Index2", strRepr=True) + \
                      source.spectrum.getFreeAttributeValueOf("name", "CutoffEnergy", strRepr=True) + source.spectrum.getFreeAttributeValueOf("name", "PivotEnergy", strRepr=True) + \
                      source.spectrum.getFreeAttributeValueOf("name", "Index", strRepr=True) + source.spectrum.getFreeAttributeValueOf("name", "Index1", strRepr=True) + \
                      str(source.spatialModel.free) + \
                      source.spectrum.getFreeAttributeValueOf("name", "Flux", strRepr=True)

        #print("bitmask:\n",bitmask)
        # '{0:08b}'.format(6)
        fixflag = int(bitmask, 2)
        #print("fixflag: ",fixflag)

        return str(fixflag)



    @staticmethod
    def _getSelectionParams(tostr = False, onlyMultiParams = False):
        sp = ["Name","Dist", "Flux", "SqrtTS"]
        if onlyMultiParams:
            sp = ["Dist", "Flux", "SqrtTS"]
        if not tostr:
            return sp
        else:
            return ' '.join(sp)

    @staticmethod
    def _getFreeParams(tostr = False):
        fp = ["Flux", "Index", "Index1", "Index2", "CutoffEnergy", "PivotEnergy", "Curvature", "Index2", "Loc"]
        if not tostr:
            return fp
        else:
            return ' '.join(fp)
