from numbers import Number

from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies
from agilepy.utils.CustomExceptions import CannotSetNotUpdatableOptionError, ConfigurationsNotValidError, OptionNameNotSupportedError

class AGAnalysisConfig():

    def checkRequiredParams(self, confDict):

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


    def completeConfiguration(self, confDict):
        CompletionStrategies._expandFileEnvVars(confDict, "evtfile")
        CompletionStrategies._expandFileEnvVars(confDict, "logfile")
        CompletionStrategies._glonDeltaIncrement(confDict)
        CompletionStrategies._convertEnergyBinsStrings(confDict)
        CompletionStrategies._convertBackgroundCoeff(confDict, "isocoeff")
        CompletionStrategies._convertBackgroundCoeff(confDict, "galcoeff")
        CompletionStrategies._setTime(confDict)
        CompletionStrategies._setPhaseCode(confDict)
        CompletionStrategies._setExpStep(confDict)
        CompletionStrategies._transformLoccl(confDict)
        return confDict


    def validateConfiguration(self, confDict):

        errors = {}

        errors.update( ValidationStrategies._validateEvtFile(confDict) )
        errors.update( ValidationStrategies._validateLogFile(confDict) )
        errors.update( ValidationStrategies._validateBackgroundCoeff(confDict) )
        errors.update( ValidationStrategies._validateIndexFiles(confDict) )
        errors.update( ValidationStrategies._validateTimeInIndex(confDict) )
        errors.update( ValidationStrategies._validateLOCCL(confDict) )
        errors.update( ValidationStrategies._validateMinMax(confDict, "selection", "fovradmin", "fovradmax") )
        errors.update( ValidationStrategies._validateMinMax(confDict, "selection", "emin", "emax") )
        errors.update( ValidationStrategies._validateTimetype(confDict))

        if errors:
            raise ConfigurationsNotValidError("Errors: {}".format(errors))


    def checkOptions(self, **kwargs):

        
        for optionName, optionValue in kwargs.items():

            if optionName == "tmin" and "timetype" not in kwargs:
                raise CannotSetNotUpdatableOptionError("The option 'tmin' can be updated if and only if you also specify the 'timetype' option.")

            if optionName == "tmax" and "timetype" not in kwargs:
                raise CannotSetNotUpdatableOptionError("The option 'tmin' can be updated if and only if you also specify the 'timetype' option.")

            if self.isHidden(optionName):
                raise CannotSetHiddenOptionError("Can't update the '{}' hidden option.".format(optionSection))


    def isHidden(self, optionName):

        if optionName in [ "lonpole", "lpointing", "bpointing", "maplistgen", "offaxisangle", \
                           "galmode2", "galmode2fit", "isomode2", "isomode2fit", "minimizertype", \
                           "minimizeralg", "minimizerdefstrategy", "mindefaulttolerance", "integratortype", \
                           "contourpoints", "edpcorrection", "fluxcorrection"]:
            return True

        return False


    def checkOptionsType(self, **kwargs):

        for optionName, optionValue in kwargs.items():
            
            # dimension / datatype
            # (int, 0) = int scalar
            # (float, 1) = float array
            # (int, 2) = int matrix
            validType = ()

            # int
            if optionName in [  "verboselvl", "filtercode", "emin", "emax", "fovradmin", \
                                "fovradmax", "albedorad", "dq", "phasecode", "expstep", \
                                "fovbinnumber", "galmode", "isomode", "emin_sources", \
                                "emax_sources", "loccl", "timeslot"]:
                
                validType = (int, 0)

            # Number (int and float)
            elif optionName in ["glat", "glon", "tmin", "tmax", "mapsize", "spectralindex", \
                                "timestep", "binsize", "ranal", "ulcl", \
                                "expratio_minthr", "expratio_maxthr", "expratio_size", "radius"]:

                validType = (Number, 0)


            # String
            elif optionName in ["evtfile", "logfile", "outdir", "filenameprefix", "logfilenameprefix", \
                                "timetype", "timelist", "projtype", "proj", "modelfile"]:

                validType = (str, 0)


            elif optionName in ["useEDPmatrixforEXP", "expratioevaluation", "twocolumns"]:

                validType = (bool, 0)


            # List of Numbers
            elif optionName in ["energybins"]:

                validType = (Number, 2)

            # List of Numbers
            elif optionName in ["galcoeff", "isocoeff"]:

                validType = (Number, 1)

            else:

                raise OptionNameNotSupportedError("Option name: {} is not supported".format(optionName))




            ValidationStrategies._validateOptionType(optionName, optionValue, validType)


    def completeUpdate(self, optionName, confDict):

        if optionName == "loccl":

            CompletionStrategies._transformLoccl(confDict)

        if optionName == "isocoeff" or optionName == "galcoeff":

            CompletionStrategies._convertBackgroundCoeff(confDict, optionName)

        if optionName == "energybins" or optionName == "fovbinnumber":

            CompletionStrategies._extendBackgroundCoeff(confDict)

        if optionName == "evtfile" or optionName == "logfile":

            CompletionStrategies._expandFileEnvVars(confDict, optionName)
