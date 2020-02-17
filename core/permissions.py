import enum


# Permission number must be 2^n
class Permission(enum.Enum):
    OWNER = 1
