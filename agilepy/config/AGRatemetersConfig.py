from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies

from numbers import Number

from agilepy.core.CustomExceptions import  CannotSetNotUpdatableOptionError, \
                                           ConfigurationsNotValidError, \
                                           OptionNameNotSupportedError, \
                                           CannotSetHiddenOptionError

                                               
class AGRatemetersConfig():
    """
    Class to configure AGRatemeters, required as it inherits by AGBaseAnalysis.
    """

    def checkRequiredParams(self, confDict):

        errors = []

        if confDict["selection"]["timetype"] is None:
            errors.append("Please, set selection/timetype (TT or UTC)")

        if confDict["selection"]["tmin"] is None:
            errors.append("Please, set selection/tmin")

        if confDict["selection"]["tmax"] is None:
            errors.append("Please, set selection/tmax")

        if errors:
            raise ConfigurationsNotValidError("{}".format(errors))
        
        return None
    
    
    def completeConfiguration(self, confDict):

        # Convert T0 from MJD to TT 
        CompletionStrategies._setT0(confDict)

        return confDict
    
    def validateConfiguration(self, confDict):

        errors = {}

        errors.update( ValidationStrategies._validateTimetype(confDict))

        return errors



    def checkOptions(self, **kwargs):

        #for optionName, optionVal in kwargs.items():

        if "tmin" in kwargs and ("timetype" not in kwargs or "tmax" not in kwargs):
            raise CannotSetNotUpdatableOptionError("The option 'tmin' can be updated if and only if you also specify the 'timetype' and 'tmax' options.")

        if "tmax" in kwargs and ("timetype" not in kwargs or "tmin" not in kwargs):
            raise CannotSetNotUpdatableOptionError("The option 'tmax' can be updated if and only if you also specify the 'timetype' and 'tmax' options.")

        return None
    

    def checkOptionsType(self, **kwargs):

        for optionName, optionValue in kwargs.items():
            
            # dimension / datatype
            # (int, 0) = int scalar
            # (float, 1) = float array
            # (int, 2) = int matrix
            validType = ()

            # int
            if optionName in ["verboselvl"]:
                
                validType = (int, 0)

            # Number (int and float)
            elif optionName in ["tmin", "tmax", "tmin_bkg", "tmax_bkg", "tmin_src", "tmax_src", "T0"]:

                validType = (Number, 0)


            # String
            elif optionName in ["evtfile", "logfile", "outdir", "timetype"]:

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
            
        return None

        

