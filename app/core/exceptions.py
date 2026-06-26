class ThirdSysError(Exception):
    pass

class ValidationError(ThirdSysError):
    pass

class DuplicateError(ThirdSysError):
    pass

class NotFoundError(ThirdSysError):
    pass