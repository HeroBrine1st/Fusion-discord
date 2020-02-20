from datetime import datetime
from termcolor import colored
from core.utils import synchronized


# noinspection PyUnusedLocal
class Logger:
    log_levels = [
        ["Verbose", None, None, None],
        ["Debug", "green", None, None],
        ["Info", "green", None, None],
        ["Warn", "yellow", None, None],
        ["Error", "red", None, None],
        ["FATAL", "grey", "on_red", None],
        ["Silent", None, None, None],
    ]

    @staticmethod
    def get_time():
        iso = datetime.now().isoformat()
        return iso[11:19]

    def __init__(self, thread="Main", app="Fusion", file=None):
        self.thread = thread
        self.app = app
        self.file = file

    @synchronized
    def raw_log(self, level: int, text: str):
        log_level = self.log_levels[level]
        _text = "[%s] [%s] [%s]: " % (
            colored(self.get_time(), "magenta"),
            colored(self.thread + " thread/" + log_level[0], log_level[1], log_level[2], log_level[3]),
            self.app)
        if level == 5:
            _text += colored(text, "red")
        else:
            _text += text
        print(_text)

    def log(self, level: int, text: str, *args):
        if args:
            text = text % tuple(args)
        for line in text.splitlines():
            self.raw_log(level, line)

    def debug(self, msg, *args, **kwargs):
        self.log(1, msg, *args)

    def info(self, msg, *args, **kwargs):
        self.log(2, msg, *args)

    def warn(self, msg, *args, **kwargs):
        self.log(3, msg, *args)

    def error(self, msg, *args, **kwargs):
        self.log(4, msg, *args)

    def fatal(self, msg, *args, **kwargs):
        self.log(5, msg, *args)

    warning = warn
    exception = error
    critical = fatal
