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

from agilepy.core.AgilepyLogger import Color 
from agilepy.utils.AstroUtils import AstroUtils
from agilepy.core.source.Spectrum import Spectrum
from agilepy.core.source.SpatialModel import SpatialModel
from agilepy.core.source.MultiAnalysis import MultiAnalysis

from agilepy.core.CustomExceptions import SelectionParamNotSupported, \
                                          SourceParameterNotFound, \
                                          NotFreeableParamsError, \
                                          SourceTypeNotSupportedError, \
                                          XMLParseError, \
                                          SourcesAgileFormatParsingError, \
                                          SourceParamNotFoundError, \
                                          MultiOutputNotFoundError

class Source:


    def __init__(self, name):
        self.name = name
        self.spectrum = None
        self.spatialModel = None
        self.multiAnalysis = MultiAnalysis()
    
    def getName(self):
        """It gets the name for the source

        Args:
           None

        Returns:
            name(str): Source name
        """
        return self.name

    def getFreeableParams(self):
        """It gets parameters to free

        Args:
           None

        Returns:
            List(str): parameters to free
        """
        return self.spectrum.getFreeableParams() + self.spatialModel.getFreeableParams()

    def setDistanceFromMapCenter(self, mapCenterL, mapCenterB):

        if self.multiAnalysis.multiDate["value"] is not None:
            sourceL = self.multiAnalysis.multiL["value"]
            sourceB = self.multiAnalysis.multiB["value"]
            if sourceL == -1:
                sourceL = self.multiAnalysis.multiStartL["value"]
            if sourceB == -1:
                sourceB = self.multiAnalysis.multiStartB["value"]
        else:
            sourceL = self.spatialModel.pos["value"][0]
            sourceB = self.spatialModel.pos["value"][1]

        self.spatialModel.dist["value"] = AstroUtils.distance(sourceL, sourceB, mapCenterL, mapCenterB)

    def getSelectionValue(self, paramName):

        paramName = paramName.lower()
    
        if paramName == "name":
            return self.name

        elif paramName == "flux":
            if self.multiAnalysis.getVal("multiDate") is not None:
                return self.get("multiFlux")["value"]
            else:
                return self.get("flux")["value"]

        elif paramName == "dist":
            if self.multiAnalysis.multiDate["value"] is not None:
                return self.get("multiDist")["value"]
            else:
                return self.get("dist")["value"]

        elif paramName == "multisqrtts" or paramName == "sqrtts":
            
            if self.multiAnalysis.getVal("multiDate") is not None:
                return self.get("multiSqrtTS")["value"]
            else:
                return None

 
        else:
            raise SelectionParamNotSupported(f"The selection parameter '{paramName}' is not supported!")



    def updateMultiAnalysis(self, multiAnalysisResult, mapCenterL, mapCenterB):
        
        # Swap last mle analysis results (if any) to spectrum and spatialModel        
        if self.multiAnalysis.multiDate["value"] is not None:

            spectrumParameters = [param["name"] for param in self.spectrum.getAttributes()]

            for spectrumParamName in spectrumParameters:
                
                # get the corresponding spectrum param name in MultiAnalysis
                multiParamName = MultiAnalysis.spectrumMultiMapping[spectrumParamName]

                # get the actual value
                multiParamValue = self.get(multiParamName)["value"]
                multiParamValueErr = self.get(multiParamName+"Err")["value"]
                
                if multiParamValue is not None:

                    self.set(spectrumParamName, {"value": multiParamValue, "err": multiParamValueErr})

    
            # New position
            self.spatialModel.pos["value"] = (self.multiAnalysis.multiLPeak["value"], self.multiAnalysis.multiBPeak["value"])

            # New distance from map center
            self.setDistanceFromMapCenter(mapCenterL, mapCenterB)


        # Override the MLE analysis results
        self.multiAnalysis = multiAnalysisResult
        


        """
        freeParams = self.getFreeParams()

        self.logger.info(self, f"{multiAnalysisResult.get('multiName')} (free) parameters update after mle: {freeParams}")

        if source.multi.get("multiL") != -1 and source.multi.get("multiB") != -1:
            oldPos = source.spatialModel.get("pos")
            newPos = Parameter("pos", "tuple<float,float>")
            newPos.setAttributes(value = f"({source.multi.multiL.value}, {source.multi.multiB.value})", free = source.spatialModel.pos.free)
            source.spatialModel.pos = newPos

            if oldPos != newPos.get():
                oldDistance = source.spatialModel.get("dist")
                
                mapCenterL = float(self.config.getOptionValue("glon"))
                mapCenterB = float(self.config.getOptionValue("glat"))
                newDistance = source.getSourceDistanceFromLB(mapCenterL, mapCenterB)
                source.spatialModel.dist.setAttributes(value = newDistance)
                source.multi.set("multiDist", newDistance)
                self.logger.info(self, f"'pos' parameter has been updated {oldPos}==>{source.spatialModel.get('pos')}")
                self.logger.info(self, f"'dist' has been updated {oldDistance}==>{source.spatialModel.get('dist')}")
            else:
                self.logger.info(self, f"'pos' parameter has not changed: {source.spatialModel.get('pos')}")

        else:
            self.logger.info(self, f"multiL,multiB=({source.multi.get('multiL')},{source.multi.get('multiB')}). 'pos' parameter has not changed: {source.spatialModel.get('pos')}")

        if "pos" in freeParams: freeParams.remove("pos")

        self.updateSpectrumParameters(source, freeParams)

    def updateSpectrumParam(self,source, multiParamName, spectrumParamName):

        if hasattr(source.spectrum, spectrumParamName):

            newVal = source.multi.get(multiParamName)
            oldVal = source.spectrum.get(spectrumParamName)

            # print(f"{multiParamName} {spectrumParamName} newVal: '{newVal}' parameter")
            # print(f"{multiParamName} {spectrumParamName} oldVal: '{oldVal}' parameter")

            if oldVal is None or newVal != oldVal:
                source.spectrum.set(spectrumParamName, newVal)
                self.logger.info(self, f"'{spectrumParamName}' parameter has been updated: {oldVal}==>{newVal}")
                # print(f"'{spectrumParamName}' parameter has been updated: {oldVal}==>{newVal}")
            else:
                self.logger.info(self, f"'{spectrumParamName}' parameter has not changed: {oldVal}==>{newVal}")
                # print(f"'{spectrumParamName}' parameter has not changed: {oldVal}==>{newVal}")


    def updateSpectrumParameters(self, source, freeParams):

            for paramName in freeParams:

                self.updateSpectrumParam(source, mapping[paramName], paramName)

            for paramName in ["fluxErr", "indexErr", "index1Err", "cutoffEnergyErr", "pivotEnergyErr", "index2Err", "curvatureErr"]:
                
                self.updateSpectrumParam(source, mapping[paramName], paramName)


    """


    @staticmethod
    def getSource(type, name):

        if type == "PointSource":
            return PointSource(name)
        else:
            raise SourceTypeNotSupportedError(f"The source type '{type}' is not supported.")

    @staticmethod
    def parseSourceXMLFormat(sourceRoot):

        if sourceRoot.tag != "source":
            raise XMLParseError(f"Tag <source> expected, '{sourceRoot.tag}' found.")

        newSource = Source.getSource(**sourceRoot.attrib)

        for sourceDescription in sourceRoot:

            if sourceDescription.tag not in ["spectrum", "spatialModel"]:
                raise XMLParseError(f"Tag <spectrum> or <spatialModel> expected, '{sourceDescription.tag}' found.")

            if sourceDescription.tag == "spectrum":

                newSource.spectrum = Spectrum.getSpectrum(sourceDescription.attrib["type"])

            if sourceDescription.tag == "spatialModel":
                
                newSource.spatialModel = SpatialModel.getSpatialModel(sourceDescription.attrib["type"])

                newSource.set("locationLimit", {'name': 'locationLimit', 'value': sourceDescription.attrib["location_limit"]})

            for parameter in sourceDescription:

                if parameter.tag != "parameter":
                    raise XMLParseError(f"Tag <parameter> expected, '{parameter.tag}' found.")

                newSource.set(parameter.attrib["name"], parameter.attrib)
        
        return newSource

    @staticmethod
    def parseSourceTXTFormat(txtLine):

        elements = [elem.strip() for elem in txtLine.split(" ") if elem] # each line is a source

        if len(elements) != 17:
            raise SourcesAgileFormatParsingError("The number of elements on the line {} is not 17, but {}".format(txtLine, len(elements)))

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

        newSource = Source.getSource(name=name, type="PointSource")

        if spectrumType == 0:
            newSource.spectrum = Spectrum.getSpectrum("PowerLaw")
        elif spectrumType == 1:
            newSource.spectrum = Spectrum.getSpectrum("PLExpCutoff")
        elif spectrumType == 2:
            newSource.spectrum = Spectrum.getSpectrum("PLSuperExpCutoff")
        elif spectrumType == 3:
            newSource.spectrum = Spectrum.getSpectrum("LogParabola")
        else:
            raise SourcesAgileFormatParsingError("spectrumType={} not supported. Supported: [0,1,2,3]".format(spectrumType))

        newSource.set("flux", {"name": "flux", "free": free_bits[0], "value": flux})

        if spectrumType == 0:

            newSource.set("index", {"name":"index", "free": free_bits[2], "scale": -1.0, "value": index, "min": float(elements[11]), "max": float(elements[12])})

        elif spectrumType == 1:

            newSource.set("index", {"name":"index", "free":free_bits[2], "scale":-1.0, "value":index, "min":float(elements[11]), "max":float(elements[12])})

            newSource.set("cutoffEnergy", {"name":"cutoffEnergy", "free":free_bits[3], "scale":-1.0, "value":float(elements[9]), "min":float(elements[13]), "max":float(elements[14])})

        elif spectrumType == 2:

            newSource.set("index1", {"name":"index1", "free":free_bits[2], "scale":-1.0, "value":index, "min":float(elements[11]), "max":float(elements[12])})

            newSource.set("cutoffEnergy", {"name":"cutoffEnergy", "free":free_bits[3], "scale":-1.0, "value":float(elements[9]), "min":float(elements[13]), "max":float(elements[14])})

            newSource.set("index2", {"name":"index2", "free":free_bits[4], "value":float(elements[10]), "min":float(elements[15]), "max":float(elements[16])})

        elif spectrumType == 3:

            newSource.set("index", {"name":"index", "free":free_bits[2], "scale":-1.0, "value":index, "min":float(elements[11]), "max":float(elements[12])})

            newSource.set("pivotEnergy", {"name":"pivotEnergy", "free":free_bits[3], "scale":-1.0, "value":float(elements[9]), "min":float(elements[13]), "max":float(elements[14])})

            newSource.set("curvature", {"name":"curvature", "free":free_bits[4], "value":float(elements[10]), "min":float(elements[15]), "max":float(elements[16])})


        newSource.spatialModel = SpatialModel.getSpatialModel("PointSource")

        newSource.set("pos", {"name":"pos", "value":f"({glon},{glat})", "free":free_bits_position})
        newSource.set("locationLimit", {"name":"locationLimit", "value":locationLimit})

        return newSource

    @staticmethod
    def fromDictionary(sourceName, dictData):

        # check type and spatial model parameters
        requiredKeys = ["glon", "glat", "spectrumType"]
        for rK in requiredKeys:
            if rK not in dictData:
                raise SourceParamNotFoundError(f"'{rK}' is a required param. Please add it to the 'sourceObject' input dictionary")

        newSource = Source.getSource(name=sourceName, type="PointSource")

        newSource.spatialModel = SpatialModel.getSpatialModel("PointSource")
        newSource.set("pos", {"value": (dictData["glon"], dictData["glat"])})
        newSource.set("locationLimit", {"value": 0})

        newSource.spectrum = Spectrum.getSpectrum(dictData["spectrumType"])

        spectrumKeys = [param["name"] for param in newSource.spectrum.getAttributes()]

        # check spectrum parameters
        for sK in spectrumKeys:
            if sK not in dictData:
                raise SourceParamNotFoundError(f"'{sK}' is a required param. Please add it to the 'sourceObject' input dictionary")

        for sK in spectrumKeys:
            newSource.set(sK, {"value": dictData[sK]})

        return newSource


class PointSource(Source):

    def __init__(self, name):
        super().__init__(name)

    def get(self, parameterName):
        """It returns a source's parameter.

        Args:
            paramName (str): the name of the source's parameter.

        Raises:
            SourceParameterNotFound: if the source's parameter is not found.

        Returns:
            The value of the source's parameter.
        
        Example:
            >>> s.get("index")
            >>> s.get("pos")
            >>> s.get("multiFlux")
        """
        if self.spectrum is not None and parameterName in vars(self.spectrum):
            return getattr(self.spectrum, parameterName)

        if self.spatialModel is not None and parameterName in vars(self.spatialModel):
            return getattr(self.spatialModel, parameterName)

        if self.multiAnalysis is not None and parameterName in vars(self.multiAnalysis):
            return getattr(self.multiAnalysis, parameterName)

        raise SourceParameterNotFound(f"Cannot perform get(), {parameterName} is not found.")
    
    
    def set(self, parameterName, attributeValueDict):
        """It sets a source's parameter.

        Args:
            parameterName (str): the name of the source's parameter.

        Returns:
            None

        Example:
            >>> s.set("index",{"value":1, "min":10})
        """

        try:
            self.spectrum.setParameter(parameterName, attributeValueDict)
        except:
            pass
        try:
            self.spatialModel.setParameter(parameterName, attributeValueDict)
        except:
            pass
        try:
            self.multiAnalysis.setParameter(parameterName, attributeValueDict)
        except:
            pass

    def getFreeParams(self):
        """It returns the source's attributes that are free to vary.

        Returns:
            The list of attributes that are free to vary.

        Example:
            >>> s.getFreeParams()
            >>> ["flux", "index"]

        """
        return self.spectrum.getFreeParams() + self.spatialModel.getFreeParams()

    def setSpectrum(self, spectrumType):
        self.spectrum = Spectrum.getSpectrum(spectrumType)

    def setSpatialModel(self, spatialModelType):
        self.spatialModel = SpatialModel.getSpatialModel(spatialModelType)

    def setMultiAnalysis(self):
        self.multiAnalysis = MultiAnalysis()
 
    def setFreeAttributeValueOf(self, parameterName, freeval):

        parameter = self.get(parameterName)

        if "free" not in parameter:
            raise NotFreeableParamsError(f"The parameter '{parameterName}' cannot be free")

        willChange = False
        if parameter["free"] != freeval:
            willChange = True
            self.set(parameterName, {"free": freeval})

        return willChange





    def bold(self, ss):
        return Color.BOLD + ss + Color.END

    def colorRed(self, ss):
        return Color.RED + ss + Color.END

    def colorBlue(self, ss):
        return Color.BLUE + ss + Color.END

    def __str__title(self):
        strr = '\n-----------------------------------------------------------'
        strr += self.bold(f'\n Source name: {self.name} ({type(self).__name__})')
        #if self.multi:
        #    strr += self.bold(" => sqrt(ts): "+str(self.multi.get("multiSqrtTS")))
        return strr        
    
    def __str__spectrumType(self):
        return f"\n  * {self.bold('Spectrum type')}: {type(self.spectrum).__name__}"

    def __str__freeParams(self):
        freeParams = self.getFreeParams()
        if len(freeParams) == 0:
            return f'\n  * {self.bold("Free parameters")}: none'
        else:
            return f'\n  * {self.bold("Free parameters")}: '+' '.join(freeParams)

    def __str__sourceParams(self):
        strr = ''
        strr += f'\n  * {self.bold("Initial source parameters")}:'

        spectrumParams = self.spectrum.getAttributes()

        for param in spectrumParams:
            
            if param["name"] == "flux":
                strr += f"\n\t- {param['name']} ({param['um']}): {param['value']:.4e}"
                if param['err'] is not None:
                    strr += f" +/- {param['err']:.4e}"
            else:
                strr += f"\n\t- {param['name']} {param['um']}: {param['value']}"
                if param['err'] is not None:
                    strr += f" +/- {param['err']}"

        
        spatialModelParams = self.spatialModel.getAttributes()

        for param in spatialModelParams:

            if param["name"] == "pos":

                strr += f"\n\t- Source position {param['um']}: {param['value']}"

            if param["name"] == "dist" and param['value'] is not None:

                strr += f"\n\t- Distance from map center ({param['um']}): {round(param['value'], 4)}"
        
        return strr
    
    
    def __str__multiAnalisys(self):

        strr = ''
        if self.multiAnalysis.multiDate["value"] is None: return strr

        strr = f'\n  * {self.bold("Last MLE analysis")} ({self.multiAnalysis.multiDate["value"]}):'

        # spectrum parameters
        # get the corresponding multi spectrum parameters
        spectrumParamsNames = [a["name"] for a in self.spectrum.getAttributes()]
        for spectrumParamName, multiSpectrumParamName in MultiAnalysis.spectrumMultiMapping.items():
            if spectrumParamName in spectrumParamsNames:
                param = self.multiAnalysis.get(multiSpectrumParamName)
                paramErr = self.multiAnalysis.get(multiSpectrumParamName+"Err")
                if spectrumParamName == "flux":
                    strr += f"\n\t- {spectrumParamName} ({param['um']}): {param['value']:.4e}"
                    if paramErr['value'] is not None:
                        strr += f" +/- {paramErr['value']:.4e}"
                else:
                    strr += f"\n\t- {spectrumParamName} {param['um']}: {param['value']}"
                    if paramErr['value'] is not None:
                        strr += f" +/- {paramErr['value']}"

        # ag_multi parameters
        strr += f'\n\t- upper limit({self.multiAnalysis.get("multiUL")["um"]}): {self.multiAnalysis.getVal("multiUL")}'

        strr += f'\n\t- ergLog(erg/cm2s): {self.multiAnalysis.getVal("multiErgLog")}'
        if self.multiAnalysis.getVal("multiErgLogErr") is not None:
            strr += f' +/- {self.multiAnalysis.getVal("multiErgLogErr")}'
        
        strr += f'\n\t- galCoeff: {self.multiAnalysis.getVal("multiGalCoeff")}'
        if self.multiAnalysis.getVal("multiGalErr") is not None and sum(self.multiAnalysis.getVal("multiGalErr")) != 0:
            strr += f' +/- {self.multiAnalysis.getVal("multiGalErr")}'
        
        strr += f'\n\t- isoCoeff: {self.multiAnalysis.getVal("multiIsoCoeff")}' 
        if self.multiAnalysis.getVal("multiIsoErr") is not None and sum(self.multiAnalysis.getVal("multiIsoErr")) != 0:
            strr += f' +/- {self.multiAnalysis.getVal("multiIsoErr")}'
        
        strr += f'\n\t- exposure({self.multiAnalysis.get("multiExp")["um"]}): {self.multiAnalysis.getVal("multiExp")}'
        strr += f'\n\t- exp-ratio: {self.multiAnalysis.getVal("multiExpRatio")}'
        strr += f'\n\t- L_peak: {self.multiAnalysis.getVal("multiLPeak")}'
        strr += f'\n\t- B_peak: {self.multiAnalysis.getVal("multiBPeak")}'
        strr += f'\n\t- Distance from start pos: {self.multiAnalysis.getVal("multiDistFromStartPositionPeak")}'
        
        strr += f'\n\t- position:'
        strr += f'\n\t    - L: {self.multiAnalysis.getVal("multiL")}'
        strr += f'\n\t    - B: {self.multiAnalysis.getVal("multiB")}'
        strr += f'\n\t    - Distance from start pos: {self.multiAnalysis.getVal("multiDistFromStartPosition")}'
        strr += f'\n\t    - radius of circle: {self.multiAnalysis.getVal("multir")}'
        strr += f'\n\t    - ellipse:'
        strr += f'\n\t\t  - a: {self.multiAnalysis.getVal("multia")}'
        strr += f'\n\t\t  - b: {self.multiAnalysis.getVal("multib")}'
        strr += f'\n\t\t  - phi: {self.multiAnalysis.getVal("multiphi")}'
        strr += '\n-----------------------------------------------------------'
        return strr
    
    def __str__(self):
        strr = ''
        strr += self.__str__title()
        strr += self.__str__spectrumType()
        strr += self.__str__freeParams()
        strr += self.__str__sourceParams()
        strr += self.__str__multiAnalisys()
        return strr

