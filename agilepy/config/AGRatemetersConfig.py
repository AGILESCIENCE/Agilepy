from astropy.time import Time
from numbers import Number
from pathlib import PosixPath

from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies
from agilepy.core.CustomExceptions import ConfigurationsNotValidError
from agilepy.utils.AstroUtils import AstroUtils

                                               
class AGRatemetersConfig():
    """
    Class to define the Configuration for AGRatemeters.
    """

    def checkRequiredParams(self, confDict):
        """Check that the required parameters are present.

        Args:
            confDict (dict): Configuration Dictionary.

        Raises:
            ConfigurationsNotValidError: Raised if one or more required keys are missing.
        """
        errors = []

        # Check required keys in "selection" section, if missing set to None
        section = confDict.setdefault("selection", {})
        required_keys = ["file_path"]
        for key in required_keys:
            section.setdefault(key, None)
        # If required keys are missing, raise an error
        errors+= [f"Please set {key}"for key in required_keys if section[key] is None]

        # Same for other sections.
        section = confDict.setdefault("analysis", {})
        required_keys = ["T0", "timetype"]
        for key in required_keys:
            section.setdefault(key, None)
        errors+= [f"Please set {key}"for key in required_keys if section[key] is None]

        # Collect Errors
        if errors:
            raise ConfigurationsNotValidError(f"{errors}")

        return None    
    
    
    def completeConfiguration(self, confDict):
        """Ensure the final configuration is complete thanks to Completion strategies.

        Args:
            confDict (dict): Configuration Dictionary.
        """
        # Complete Selection section with default values
        sectionDict = confDict['selection']
        sectionDict['file_path'] = CompletionStrategies._expandEnvironmentalVariable(sectionDict['file_path'])

        # Complete Analysis section with default values
        sectionDict = confDict['analysis']
        sectionDict.setdefault("background_tmin", None)
        sectionDict.setdefault("background_tmax", None)
        sectionDict.setdefault("signal_tmin", None)
        sectionDict.setdefault("signal_tmax", None)
        
        # Convert T0 to AGILE seconds (TT)
        if confDict['analysis']['timetype'].upper() == "TT" or confDict['analysis']['timetype'].upper() == "OBT":
            confDict['analysis']['timetype'] = "TT"
        else:
            t = Time(confDict['analysis']['T0'], format=confDict['analysis']['timetype'])
            confDict['analysis']['T0'] = AstroUtils.convert_time_to_agile_seconds(t)
            confDict['analysis']['timetype'] = "TT"

        return confDict
    
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
        """Check that the options belong to the correct type.

        Raises:
            OptionNameNotSupportedError: Option not supported for this class.
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
            elif optionName in ["background_tmin", "background_tmax", "signal_tmin", "signal_tmax", "T0"]:
                validType = (Number, 0)
            # String
            elif optionName in ["logfile", "filenameprefix", "logfilenameprefix", "sourcename", "username", "file_path", "timetype"]:
                validType = (str, 0)
            # Path
            elif optionName in ["outdir"]:
                validType = (PosixPath, 0)
            # Bool
            elif optionName in []:
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
            keysNotAllowedToBeNone = ["T0","timetype","file_path"]
            if (optionValue is None) and (optionName not in keysNotAllowedToBeNone):
                continue
            # Check the type
            ValidationStrategies._validateOptionType(optionName, optionValue, validType)


    def completeUpdate(self, optionName, confDict):
        pass

