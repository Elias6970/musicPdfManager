
from backend.app.models.presets.resolution_preset import UnresolvedInstrumentResponse

class FileCouldNotBeReadException(Exception):
    pass

class CodAlreadyExistsError(Exception):
    pass

class PieceCodAlreadyExistsError(Exception):
    pass

class PieceNameAlreadyExistsError(Exception):
    pass

class EmailAlreadyRegisteredError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class InvalidUserDataError(Exception):
    pass

class InsufficientPermissionsError(Exception):
    pass

class UnresolvedInstrumentsException(Exception):
    def __init__(self, unresolved: list["UnresolvedInstrumentResponse"]):
        #List of UnresolvedInstrumentResponse
        self.unresolved = unresolved
        super().__init__(f"{len(unresolved)} unresolved instruments found.")

class FileTooLargeException(Exception):
    pass

class UserConfigNotFoundError(Exception):
    pass

class PresetNotFoundError(Exception):
    pass

class PresetAlreadyExistsError(Exception):
    pass

class ClassificationFileExistsError(Exception):
    def __init__(self, message: str, incorrect_keys: list[str]):
        super().__init__(message)
        self.incorrect_keys = incorrect_keys

class RoleNameAlreadyExistsError(Exception):
    pass

class RoleNotFoundError(Exception):
    pass