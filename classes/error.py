
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