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
    pass


class AccessDeniedException(CommandException):
    pass
