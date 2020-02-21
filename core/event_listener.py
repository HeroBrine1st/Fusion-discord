import enum


class Priority(enum.Enum):
    LOW = -10
    NORMAL = 0
    HIGH = 10


def EventListener(func=None, priority=Priority.NORMAL):
    if callable(func):
        func.priority = priority.value
        return func
    else:
        def decorator(func):
            func.priority = priority.value
            return func

        return decorator
