from enum import Enum


class CommandResult(Enum):
    success = "success"
    arguments_insufficient = "Insufficient arguments"
