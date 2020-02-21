class EventListener:
    def __new__(cls, func):
        if callable(func):
            func.priority = 0
            return func
        else:
            return cls

    def __init__(self, priority=0):
        self.priority = priority

    def __call__(self, func):
        func.priority = self.priority
        return func
