import threading

from bot.settings import args_regex
from core.exceptions import ParseError


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def arg_parse(arg):
    arg = str(arg)
    try:
        result = float(arg)
    except ValueError:
        al = arg.lower()
        if al == "t" or al == "true":
            return True
        elif al == "f" or al == "false":
            return False
        else:
            return arg
    else:
        try:
            result = int(arg)
        except ValueError:
            pass
    return result


def parse(raw):
    args = []
    kwargs = DotDict()
    skip = -1
    for i, elem in enumerate(raw):
        if i <= skip:
            continue
        if elem.startswith("--"):
            elem = elem[2:]
            key, value = elem, True
            if ~elem.find("="):
                res = args_regex.search(elem)
                key = res.group(1)
                value = res.group(2)
                if value.startswith("\"") and value.count("\"") == 1:
                    for j, elem_2 in enumerate(raw[i + 1:]):
                        value += " " + elem_2
                        if elem_2.count("\"") == 1 and elem_2.endswith("\""):
                            break
                        elif elem_2.count("\"") > 0:
                            raise ParseError("Unclosed quote")
                        skip = j + i + 2
                    if not value.endswith("\""):
                        raise ParseError("Unclosed quote")
                    value = value[1:-1]
            kwargs[key] = arg_parse(value)
        elif elem.startswith("-"):
            for char in elem[1:]:
                kwargs[char] = True
        else:
            args.append(arg_parse(elem))
    return args, kwargs
