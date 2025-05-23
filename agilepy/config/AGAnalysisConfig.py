from numbers import Number

from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies
from agilepy.core.CustomExceptions import  CannotSetNotUpdatableOptionError, \
                                           ConfigurationsNotValidError, \
                                           OptionNameNotSupportedError, \
                                           CannotSetHiddenOptionError

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
        CompletionStrategies._expandFileEnvVars(confDict, "datapath")
        CompletionStrategies._glonDeltaIncrement(confDict)
        CompletionStrategies._convertEnergyBinsStrings(confDict)
        CompletionStrategies._convertBackgroundCoeff(confDict, "isocoeff")
        CompletionStrategies._convertBackgroundCoeff(confDict, "galcoeff")
        CompletionStrategies._setTime(confDict)
        CompletionStrategies._setPhaseCode(confDict)
        CompletionStrategies._setExpStep(confDict)
        CompletionStrategies._transformLoccl(confDict)
        CompletionStrategies._dqCompletion(confDict)
        CompletionStrategies._completeDatapathForRest(confDict)
        return confDict


    def validateConfiguration(self, confDict):

        errors = {}

        errors.update(ValidationStrategies._validateVerboseLvl(confDict))
        #errors.update( ValidationStrategies._validateEvtFile(confDict) ) deprecated
        #errors.update( ValidationStrategies._validateLogFile(confDict) ) deprecated
        errors.update( ValidationStrategies._validateBackgroundCoeff(confDict) )
        errors.update( ValidationStrategies._validateIndexFiles(confDict) )
        #errors.update( ValidationStrategies._validateTimeInIndex(confDict) )
        errors.update( ValidationStrategies._validateLOCCL(confDict) )
        errors.update( ValidationStrategies._validateMinMax(confDict, "selection", "fovradmin", "fovradmax") )
        errors.update( ValidationStrategies._validateTimetype(confDict))
        errors.update( ValidationStrategies._validateFluxcorrection(confDict) )
        #errors.update( ValidationStrategies._validateAlbedorad(confDict) )
        #errors.update( ValidationStrategies._validateFovradmax(confDict) )
        errors.update( ValidationStrategies._validateDQ(confDict) )
        errors.update(ValidationStrategies._validateDatapath(confDict))
        errors.update(ValidationStrategies._validateIrf(confDict, "selection", "irf"))
        errors.update(ValidationStrategies._validateDeprecatedOptions(confDict))


        return errors


    def checkOptions(self, **kwargs):

        #for optionName, optionVal in kwargs.items():

        if "tmin" in kwargs and ("timetype" not in kwargs or "tmax" not in kwargs):
            raise CannotSetNotUpdatableOptionError("The option 'tmin' can be updated if and only if you also specify the 'timetype' and 'tmax' options.")

        if "tmax" in kwargs and ("timetype" not in kwargs or "tmin" not in kwargs):
            raise CannotSetNotUpdatableOptionError("The option 'tmax' can be updated if and only if you also specify the 'timetype' and 'tmax' options.")

        if ("albedorad" in kwargs or "fovradmax" in kwargs) and "dq" not in kwargs:
            raise CannotSetNotUpdatableOptionError(
                    "You cannot set albedorad or fovradmax without setting dq = 0")
        elif ("albedorad" in kwargs or "fovradmax" in kwargs) and kwargs["dq"] != 0:
            raise CannotSetNotUpdatableOptionError(
                "The options 'albedorad' and 'fovradmax' can be updated if and only when dq = 0.")

        if "dq" in kwargs and kwargs["dq"] == 0 and ("albedorad" not in kwargs and "fovradmax" not in kwargs):
            raise CannotSetNotUpdatableOptionError("The option 'dq' can be 0 if and only if you also specify the 'albedorad' and 'fovradmax' options.")
            
            



    def checkOptionsType(self, **kwargs):

        for optionName, optionValue in kwargs.items():
            
            # dimension / datatype
            # (int, 0) = int scalar
            # (float, 1) = float array
            # (int, 2) = int matrix
            validType = ()

            # int
            if optionName in [  "verboselvl", "filtercode", "fovradmin", \
                                "fovradmax", "albedorad", "dq", "phasecode", "expstep", \
                                "fovbinnumber", "galmode", "isomode", "loccl", "timeslot", "fluxcorrection", \
                                "minimizerdefstrategy", "integratortype", "contourpoints",
                                "galmode2", "galmode2fit", "isomode2", "isomode2fit", "lonpole" \
                                ]:
                
                validType = (int, 0)

            # Number (int and float)
            elif optionName in ["glat", "glon", "tmin", "tmax", "mapsize", "spectralindex", \
                                "timestep", "binsize", "ranal", "ulcl", \
                                "expratio_minthr", "expratio_maxthr", "expratio_size", "radius", \
                                "edpcorrection", "mindefaulttolerance", "offaxisangle", "lpointing", \
                                "bpointing"]:

                validType = (Number, 0)


            # String
            elif optionName in ["evtfile", "logfile", "outdir", "filenameprefix", "logfilenameprefix", \
                                "timetype", "timelist", "projtype", "proj", "modelfile", "minimizertype", \
                                "minimizeralg", "maplistgen", "irf"]:

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
        
        if optionName == "dq":

            CompletionStrategies._dqCompletion(confDict)

        


