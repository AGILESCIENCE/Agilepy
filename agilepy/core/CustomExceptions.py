class AGILENotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class PFILESNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ScienceToolInputArgMissing(Exception):
    def __init__(self, message):
        super().__init__(message)

class MaplistIsNone(Exception):
    def __init__(self, message):
        super().__init__(message)

class SourceModelFormatNotSupported(Exception):
    def __init__(self, message):
        super().__init__(message)

class FileSourceParsingError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SourceNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

class ScienceToolProductNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

class ScienceToolErrorCodeReturned(Exception):
    def __init__(self, message):
        super().__init__(message)

class SelectionStringToLambdaConversioFailed(Exception):
    def __init__(self, message):
        super().__init__(message)

class SelectionParamNotSupported(Exception):
    def __init__(self, message):
        super().__init__(message)

class EnvironmentVariableNotExpanded(Exception):
    def __init__(self, message):
        super().__init__(message)

class ConfigurationsNotValidError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SourcesFileLoadingError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SourcesAgileFormatParsingError(Exception):
    def __init__(self, message):
        super().__init__(message)

class OptionNotFoundInConfigFileError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ConfigFileOptionTypeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class DeprecatedOptionError(Exception):
    def __init__(self, message):
        super().__init__(message)

class CannotSetHiddenOptionError(Exception):
    def __init__(self, message):
        super().__init__(message)

class CannotSetNotUpdatableOptionError(Exception):
    def __init__(self, message):
        super().__init__(message)

class LoggerTypeNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

class WrongCoordinateSystemError(Exception):
    def __init__(self, message):
        super().__init__(message)

class WrongSpatialModelTypeError(Exception):
    def __init__(self, message):
        super().__init__(message)

class AttributeValueDatatypeNotSupportedError(Exception):
    def __init__(self, message):
        super().__init__(message)

class NotFreeableParamsError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SourceParamNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SpectrumTypeNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class MultiOutputNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class AnalysisClassNotSupported(Exception):
    def __init__(self, message):
        super().__init__(message)

class OptionNameNotSupportedError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SourcesLibraryIsEmpty(Exception):
    def __init__(self, message):
        super().__init__(message)

class ValueOutOfRange(Exception):
    def __init__(self, message):
        super().__init__(message)

class SourceParameterNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

class ParameterNotManuallyUpdatable(Exception):
    def __init__(self, message):
        super().__init__(message)

class AttributeNotSupportedError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SourceTypeNotSupportedError(Exception):
    def __init__(self, message):
        super().__init__(message)

class XMLParseError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SSDCRestErrorDownload(Exception):
    def __init__(self, message):
        super().__init__(message)

class NoCoverageDataError(Exception):
    def __init__(self, message):
        super().__init__(message)
