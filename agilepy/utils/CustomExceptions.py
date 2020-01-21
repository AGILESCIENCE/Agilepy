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
