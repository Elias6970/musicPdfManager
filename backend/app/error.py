
class PdfNotFoundException(Exception):
    pass

class EmptyInitialInputException(Exception):
    pass

class NoMorePiecesToClassifyException(Exception):
    pass

class FirstPageException(Exception):
    pass

class PathNotFoundException(Exception):
    pass

class NoScoresException(Exception):
    pass

class PieceNotFoundException(Exception):
    pass

class AvoidModificationException(Exception):
    pass

class StopClassifyingException(Exception):
    pass

class MoreScoresThanPresetsException(Exception):
    pass

class FileCouldNotBeReadException(Exception):
    pass

class IncorrectCodOrNameError(Exception):
    pass

class CodAlreadyExistsError(Exception):
    pass

class EmailAlreadyRegisteredError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class InvalidUserDataError(Exception):
    pass