from astropy.time import Time
from numbers import Number
from pathlib import PosixPath

from agilepy.config.ValidationStrategies import ValidationStrategies
from agilepy.config.CompletionStrategies import CompletionStrategies
from agilepy.core.CustomExceptions import ConfigurationsNotValidError, CannotSetNotUpdatableOptionError
from agilepy.utils.AstroUtils import AstroUtils

class AGVisibilityConfig:
    """Class to define the Configuration for AGVisibility.
    """
    
    def checkRequiredParams(self, confDict):
        """Check that the required parameters are present.

        Args:
            confDict (dict): Configuration Dictionary.

        Raises:
            ConfigurationsNotValidError: Raised if one or more required keys are missing.
        """
        errors = []

        # Check required keys in "input" section, if missing set to None
        section = confDict.setdefault("input", {})
        required_keys = ["logfile"]
        for key in required_keys:
            section.setdefault(key, None)
        # If required keys are missing, raise an error
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
        # Complete section with default values: Input
        sectionDict = confDict['input']
        sectionDict['logfile'] = CompletionStrategies._expandEnvironmentalVariable(sectionDict['logfile'])
        sectionDict['fermi_spacecraft_file'] = sectionDict.setdefault("fermi_spacecraft_file", None)
        if sectionDict['fermi_spacecraft_file'] is not None:
            sectionDict['fermi_spacecraft_file'] = CompletionStrategies._expandEnvironmentalVariable(sectionDict['fermi_spacecraft_file'])
        
        # Complete section with default values: Selection
        sectionDict = confDict['selection']
        CompletionStrategies._setDefaultValueNotNone(sectionDict, "zmax", 180.0)
        CompletionStrategies._setDefaultValueNotNone(sectionDict, "step",  30.0)
        
        CompletionStrategies._setDefaultValueNotNone(sectionDict, "tmin",   9469440)
        CompletionStrategies._setDefaultValueNotNone(sectionDict, "tmax", 632620800)
        CompletionStrategies._setDefaultValueNotNone(sectionDict, "timetype", "TT")
        # Check that Tmin<Tmax
        if sectionDict['tmin']>=sectionDict['tmax']:
            raise ConfigurationsNotValidError(f"Tmin must be < Tmax. Provided Tmin={sectionDict['tmin']}, Tmax={sectionDict['tmax']}")
        # Convert tmin, tmax to AGILE seconds (TT)
        if not (confDict['selection']['timetype'].upper() == "TT" or confDict['selection']['timetype'].upper() == "OBT"):
            t = Time(confDict['selection']['tmin'], format=confDict['selection']['timetype'])
            confDict['selection']['tmin'] = AstroUtils.convert_time_to_agile_seconds(t)
            t = Time(confDict['selection']['tmax'], format=confDict['selection']['timetype'])
            confDict['selection']['tmax'] = AstroUtils.convert_time_to_agile_seconds(t)
        confDict['selection']['timetype'] = "TT"
        
        # Complete section with default values: Source
        sectionDict = confDict['source']
        sectionDict['coord1'] = sectionDict.setdefault("coord1", None)
        sectionDict['coord2'] = sectionDict.setdefault("coord2", None)
        sectionDict['frame' ] = sectionDict.setdefault("frame", "icrs")
        
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
        for _, v in confDict.items():
            if isinstance(v, dict):
                self.checkOptions(**v)

        return errors

    def checkOptions(self, **kwargs):
        """Check combinations of parameters.

        Raises:
            CannotSetNotUpdatableOptionError: Exception if parameters cannot be updated.
        """
        # Tmin, Tmax and timetype must be updated together
        if (("tmin" in kwargs) and ("timetype" not in kwargs)) or (("tmin" not in kwargs) and ("timetype" in kwargs)):
            raise CannotSetNotUpdatableOptionError(f"The options \'tmin\' and \'timetype\' can only be updated together.")
        if (("tmax" in kwargs) and ("timetype" not in kwargs)) or (("tmax" not in kwargs) and ("timetype" in kwargs)):
            raise CannotSetNotUpdatableOptionError(f"The options \'tmax\' and \'timetype\' can only be updated together.")
        
        # If Tmin and Tmax are updated (together), check that Tmin<Tmax
        if (("tmin" in kwargs) and ("tmax" not in kwargs)) or (("tmax" in kwargs) and ("tmin" not in kwargs)):
            raise CannotSetNotUpdatableOptionError(f"The options \'tmin\' and \'tmax\' can only be updated together.")
        elif ("tmin" in kwargs) and ("tmax" in kwargs):
            if kwargs["tmin"] >= kwargs["tmax"]:
                raise CannotSetNotUpdatableOptionError(f"tmin ({kwargs['tmin']}) must be less than tmax ({kwargs['tmax']}).")

        return None

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
            
            # Int
            if optionName in ["verboselvl"]:
                validType = (int, 0)
            # Number (int and float)
            elif optionName in ["tmin", "tmax", "zmax", "step", "coord1", "coord2"]:
                validType = (Number, 0)
            # String
            elif optionName in ["filenameprefix", "sourcename", "username", "logfile", "fermi_spacecraft_file", "timetype", "frame"]:
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
            keysNotAllowedToBeNone = ["logfile","zmax","step","tmin","tmax","timetype"]
            if (optionValue is None) and (optionName not in keysNotAllowedToBeNone):
                continue
            # Check the type
            ValidationStrategies._validateOptionType(optionName, optionValue, validType)

    def completeUpdate(self, optionName, confDict):
        pass

