from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies

class AGAnalysisConfig():

    
    @staticmethod
    def checkRequiredParams(confDict):

        errors = []

        if confDict["input"]["evtfile"] is None:
            errors.append("Please, set input/evtfile")

        if confDict["input"]["logfile"] is None:
            errors.append("Please, set input/logfile")

        if confDict["selection"]["timetype"] is None:
            errors.append("Please, set selection/timetype (MJD or TT)")

        if confDict["selection"]["tmin"] is None:
            errors.append("Please, set selection/tmin")

        if confDict["selection"]["tmax"] is None:
            errors.append("Please, set selection/tmax")

        if confDict["selection"]["glon"] is None:
            errors.append("Please, set selection/glon")

        if confDict["selection"]["glat"] is None:
            errors.append("Please, set selection/glat")

        if errors:
            raise ConfigurationsNotValidError("{}".format(errors))

    @staticmethod
    def completeConfiguration(confDict):
        CompletionStrategies._expandEvtfileEnvVars(confDict)
        CompletionStrategies._expandLogfileEnvVars(confDict)
        CompletionStrategies._glonDeltaIncrement(confDict)
        CompletionStrategies._convertEnergyBinsStrings(confDict)
        CompletionStrategies._convertBackgroundCoeff(confDict, "isocoeff")
        CompletionStrategies._convertBackgroundCoeff(confDict, "galcoeff")
        CompletionStrategies._setTime(confDict)
        CompletionStrategies._setPhaseCode(confDict)
        CompletionStrategies._setExpStep(confDict)
        CompletionStrategies._transformLoccl(confDict)
        return confDict

    @staticmethod
    def validateConfiguration(confDict):

        errors = {}

        errors.update( ValidationStrategies._validateBackgroundCoeff(confDict) )
        errors.update( ValidationStrategies._validateIndexFiles(confDict) )
        errors.update( ValidationStrategies._validateTimeInIndex(confDict) )
        errors.update( ValidationStrategies._validateLOCCL(confDict) )
        errors.update( ValidationStrategies._validateMinMax(confDict, "selection", "fovradmin", "fovradmax") )
        errors.update( ValidationStrategies._validateMinMax(confDict, "selection", "emin", "emax") )
        errors.update( ValidationStrategies._validateTimetype(confDict))

        if errors:
            raise ConfigurationsNotValidError("Errors: {}".format(errors))
