from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies

class AGEngAgileOffaxisVisibilityConfig:
    
    def checkRequiredParams(self, confDict):
        pass
    
    def completeConfiguration(self, confDict):
        pass

    def validateConfiguration(self, confDict):
        pass


    def checkOptionsType(self, **kwargs):

        for optionName, optionValue in kwargs.items():
            
            # dimension / datatype
            # (int, 0) = int scalar
            # (float, 1) = float array
            # (int, 2) = int matrix
            validType = ()

            # String
            if optionName in ["logfile", "outdir", "filenameprefix"]:

                validType = (str, 0)

            else:

                validType = (None, None)
    


            ValidationStrategies._validateOptionType(optionName, optionValue, validType)

    def completeUpdate(self, optionName, confDict):
        pass