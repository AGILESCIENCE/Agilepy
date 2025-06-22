from numbers import Number
from pathlib import PosixPath

from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies
from agilepy.core.CustomExceptions import ConfigurationsNotValidError

class AGBayesianBlocksConfig():
    """
    Class to define the Configuration for AGBayesianBlocks
    """

    def checkRequiredParams(self, confDict):
        """Check thats the required parameters are present."""
        errors = []
        
        # Check required keys in "selection" section, if missing set to None
        selection = confDict.setdefault("selection", {})
        required_keys = ["file_path", "file_mode"]
        for key in required_keys:
            selection.setdefault(key, None)
        # If required keys are missing, raise an error
        errors+= [f"Please set {key}"for key in required_keys if selection[key] is None]

        # Same for "bayesianblocks" section
        _ = confDict.setdefault("bayesianblocks", {})

        # Collect Errors
        if errors:
            raise ConfigurationsNotValidError(f"{errors}")
        
        return None
    
    
    def completeConfiguration(self, confDict):
        """Ensure the final configuration is complete thanks to Completion strategies"""
        # Complete Selection section with default values
        sectionDict = confDict['selection']
        sectionDict['file_path'] = CompletionStrategies._expandEnvironmentalVariable(sectionDict['file_path'])
        CompletionStrategies._setDefaultValueNotNone(sectionDict, "ratecorrection", 0)
        sectionDict.setdefault("tstart", None)
        sectionDict.setdefault("tstop", None)
        
        # Complete Bayesian Blocks section with default values
        sectionDict = confDict['bayesianblocks']
        CompletionStrategies._setDefaultValueNotNone(sectionDict, "useerror", True)
        CompletionStrategies._setDefaultValueNotNone(sectionDict, "fitness", "events")
        sectionDict.setdefault("gamma", None)
        sectionDict.setdefault("p0", None)
        
        return None
    
    
    def validateConfiguration(self, confDict):
        """Enact the Validation Strategies for the Configuration."""
        errors = {}
        errors.update(ValidationStrategies._validateVerboseLvl(confDict))
        errors.update(ValidationStrategies._validateDeprecatedOptions(confDict))
        
        # Check Options Type for each section of ConfDict
        for _, v in confDict.items():
            if isinstance(v, dict):
                self.checkOptionsType(**v)
        
        # Check Options Restricted combinations
        # for k, v in confDict.items():
        #     if isinstance(v, dict):
        #         self.checkOptions(**v)
        
        return errors
    
    
    def checkOptions(self, **kwargs):
        """Check combinations of parameters."""

    def checkOptionsType(self, **kwargs):
        """
        Check that the options belong to the correct type.
        """
        
        # validType tuples = (datatype, dimension)
        # (int, 0) = int scalar
        # (float, 1) = float array
        # (int, 2) = int matrix

        for optionName, optionValue in kwargs.items():
            
            validType = ()
            
            # Int
            if optionName in ["verboselvl"]:
                validType = (int, 0)
            # Number (int and float)
            elif optionName in ["ratecorrection", "tstart", "tstop", "p0", "gamma"]:
                validType = (Number, 0)
            # String
            elif optionName in ["logfile", "filenameprefix", "logfilenameprefix", "sourcename", "username",
                                "file_path", "file_mode", "fitness",
                                ]:
                validType = (str, 0)
            # Path
            elif optionName in ["outdir"]:
                validType = (PosixPath, 0)
            # Bool
            elif optionName in ["useerror"]:
                validType = (bool, 0)
            # List of Numbers
            elif optionName in []:
                validType = (Number, 1)
            # List of List of Numbers
            elif optionName in []:
                validType = (Number, 2)
            # Else
            else:
                validType = (None, None)
                #raise OptionNameNotSupportedError(f"Option name: {optionName} is not supported")
    
            # Do not check for None options
            keysNotAllowedToBeNone = ["useerror","fitness"]
            if (optionValue is None) and (optionName not in keysNotAllowedToBeNone):
                continue
            # Check the type
            ValidationStrategies._validateOptionType(optionName, optionValue, validType)

    def completeUpdate(self, optionName, confDict):
        pass