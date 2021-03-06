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


def quote_count(value):
    return value.count("\"") - value.count("\\\"")


def parse_quotes(value, raw):
    if len(raw) == 0:
        raise ParseError("Unclosed quote")
    i = 0
    for i, elem in enumerate(raw):
        value += " " + elem
        if quote_count(elem) == 1 and elem.endswith("\"") and not elem.endswith("\\\""):
            break
        elif quote_count(elem) > 0:
            raise ParseError("Unclosed quote")
    if not value.endswith("\""):
        raise ParseError("Unclosed quote")
    return i, value


def parse(raw):  # Огромный (во всех смыслах) костыль. Нужно отрефакторить на регексы
    args = []
    kwargs = DotDict()
    skip = -1
    if quote_count(" ".join(raw)) & 1 == 1:  # Verify that quote count is 2n
        raise ParseError("Unclosed quote")
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
                if value.startswith("\""):
                    if quote_count(value) == 1:
                        skip_1, parsed = parse_quotes(value, raw[i + 1:])
                        skip = i + skip_1 + 1
                        value = parsed[1:-1]
                    elif value.endswith("\"") and not value.endswith("\\\""):
                        value = value[1:-1]
            kwargs[key] = arg_parse(value)
        elif elem.startswith("-"):
            for char in elem[1:]:
                if char == "\"":
                    raise ParseError("Quote can't be in char statement")
                kwargs[char] = True
        else:
            if elem.startswith("\""):
                if quote_count(elem) == 1:
                    skip_1, parsed = parse_quotes(elem, raw[i + 1:])
                    skip = i + skip_1 + 1
                    elem = parsed[1:-1]
                elif elem.endswith("\"") and not elem.endswith("\\\""):
                    elem = elem[1:-1]
            args.append(arg_parse(elem))
    return args, kwargs
