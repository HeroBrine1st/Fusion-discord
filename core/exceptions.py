class SocketClosedException(Exception):
    pass


class OpenComputersError(Exception):
    error: str

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.error


class RequestObtainException(Exception):
    pass


class CommandException(Exception):
    def __init__(self, error, title="При обработке ввода произошла ошибка"):
        self.error = error
        self.title = title

    def __str__(self):
        return self.error


class AccessDeniedException(CommandException):
    pass


class ParseError(Exception):
    pass
