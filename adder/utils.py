class AdderError(Exception):
    pass

class InvalidArgumentError(AdderError):
    pass

class ParsingError(AdderError):
    pass