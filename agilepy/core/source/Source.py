from agilepy.core.AgilepyLogger import Color 
from agilepy.core.source.Spectrum import Spectrum
from agilepy.core.source.SpatialModel import SpatialModel
from agilepy.core.source.MultiAnalysis import MultiAnalysis

from agilepy.core.CustomExceptions import SourceParameterNotFound, NotFreeableParamsError

class Source:

    def __init__(self):
        self.name = None

    def setName(self, name):
        self.name = name
    
    def getName(self):
        return self.name

class PointSource(Source):

    def __init__(self):
        self.spectrum = None
        self.spatialModel = None
        self.multiAnalysis = None

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



    def setSpectrum(self, spectrumType):
        self.spectrum = Spectrum.getSpectrum(spectrumType)

    def setSpatialModel(self, spatialModelType):
        self.spatialModel = SpatialModel.getSpatialModel(spatialModelType)

    def setMultiAnalysis(self):
        self.multiAnalysis = MultiAnalysis()

    def getFreeParams(self):
        """It returns the source's attributes that are free to vary.

        Returns:
            The list of attributes that are free to vary.

        Example:
            >>> s.getFreeParams()
            >>> ["flux", "index"]

        """
        return self.spectrum.getFreeParams() + self.spatialModel.getFreeParams()
        
 
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
        strr += self.bold(f'\n Source name: {self.name} ({type(self)})')
        #if self.multi:
        #    strr += self.bold(" => sqrt(ts): "+str(self.multi.get("multiSqrtTS")))
        return strr        

    def __str__freeParams(self):
        freeParams = self.getFreeParams()
        if len(freeParams) == 0:
            return f'\n  * {self.bold("Free parameters")}: none'
        else:
            return f'\n  * {self.bold("Free parameters")}: '+' '.join(freeParams)

    def __str__sourceParams(self):
        strR = ''
        strR += f'\n  * {self.bold("Initial source parameters")}: ({self.initialSpectrum.stype})'

        spectrumParams = Spectrum.getSpectrumParamsNames(self.initialSpectrum.stype)

        for i, paramName in enumerate(spectrumParams):
            
            # end of the list
            if i+1 == len(spectrumParams):
                break
            
            # print only params not errors
            if i % 2 == 0:
                pn = paramName
                if paramName == "flux":
                    pn += "(ph/cm2s)"
                strR += f"\n\t- {pn}: {str(self.initialSpectrum.get(paramName))}"
                if self.initialSpectrum.get(spectrumParams[i+1]):
                    strR += f" +/- {str(self.initialSpectrum.get(spectrumParams[i+1]))}"

        strR += f"\n\t- Source position: {self.initialSpatialModel.get('pos')} (l,b)"
        
        strR += f"\n\t- Distance from map center: {round(self.initialSpatialModel.get('dist'), 4)} deg"

        return strR
    
    """
    def __str__multiAnalisys(self):
        strr = ''
        if self.multi is None:
            return strr

        # freeParams = self.getFreeParams()

        ## Multi
        if self.multi:

            strr = f'\n  * {self.bold("Last MLE analysis")}:'
            
            # spectrum parameters
            for key,val in self.spectrum.getParameters().items():
                strr += f'\n\t- {key}: {val[0]}'
                if val[1]:
                    strr += f" +/- {val[1]}"
            
            # ag_multi parameters
            strr += f'\n\t- upper limit(ph/cm2s): {self.multi.get("multiUL")}'
            strr += f'\n\t- ergLog(erg/cm2s): {self.multi.get("multiErgLog")}'
            if self.multi.get("multiErgLogErr"):
                strr += f' +/- {self.multi.get("multiErgLogErr")}'
            strr += f'\n\t- galCoeff: {self.multi.get("multiGalCoeff")}'
            if self.multi.get("multiGalErr") and sum(self.multi.get("multiGalErr")) != 0:
                strr += f' +/- {self.multi.get("multiGalErr")}'
            strr += f'\n\t- isoCoeff: {self.multi.get("multiIsoCoeff")}' 
            if self.multi.get("multiIsoErr") and sum(self.multi.get("multiIsoErr")) != 0:
                strr += f' +/- {self.multi.get("multiIsoErr")}'
            strr += f'\n\t- exposure(cm2s): {self.multi.get("multiExp")}'
            strr += f'\n\t- exp-ratio: {self.multi.get("multiExpRatio")}'
            strr += f'\n\t- L_peak: {self.multi.get("multiLPeak")}'
            strr += f'\n\t- B_peak: {self.multi.get("multiBPeak")}'
            strr += f'\n\t- Distance from start pos: {self.multi.get("multiDistFromStartPositionPeak")}'
            strr += f'\n\t- position:'
            strr += f'\n\t    - L: {self.multi.get("multiL")}'
            strr += f'\n\t    - B: {self.multi.get("multiB")}'
            strr += f'\n\t    - Distance from start pos: {self.multi.get("multiDistFromStartPosition")}'
            strr += f'\n\t    - radius of circle: {self.multi.get("multir")}'
            strr += f'\n\t    - ellipse:'
            strr += f'\n\t\t  - a: {self.multi.get("multia")}'
            strr += f'\n\t\t  - b: {self.multi.get("multib")}'
            strr += f'\n\t\t  - phi: {self.multi.get("multiphi")}'


        strr += '\n-----------------------------------------------------------'
        return strr
    """
    def __str__(self):
        strr = ''
        strr += self.__str__title()
        strr += self.__str__freeParams()
        #strr += self.__str__sourceParams()
        #strr += self.__str__multiAnalisys()
        return strr








if __name__=='__main__':

    s = PointSource()
    s.setName("2AGLJ2254+1609")
    s.setSpectrum("PowerLaw")
    s.setSpatialModel("PointSource")
    s.setMultiAnalysis()

    print(s.get("index"))
    print(s.get("pos"))
    print(s.get("multiFlux"))

    s.set("index", {"value": 10, "min": 1000})
    print(s.get("index"))
    s.set("index", {"value": 16, "max": 42})
    print(s.get("index"))

    print(s)

    s.setFreeAttributeValueOf("index", True)
    s.setFreeAttributeValueOf("flux", True)

    print(s)
