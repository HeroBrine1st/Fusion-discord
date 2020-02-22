# https://gist.github.com/SegFaultAX/629a3a8c15b0fd188000

SPECIAL_DELIM = [("[{}[".format("=" * n), "]{}]".format("=" * n)) for n in range(10)]


def type_of(v, *types):
    return any(isinstance(v, t) for t in types)


def get_delim(s):
    if '"' not in s and "\n" not in s:
        return '"', '"'
    for op, cl in SPECIAL_DELIM:
        if op not in s and cl not in s:
            return op, cl
    raise ValueError("could not find delimiter for string")


def indent(s, level, prefix="  "):
    return "\n".join("{}{}".format(prefix * level, elem).rstrip() for elem in s.split("\n"))


def to_lua(value):
    if type_of(value, str):
        od, cd = get_delim(value)
        temp = "{}{}{}".format(od, value, cd)
    elif type_of(value, float, int):
        temp = "{}".format(value)
    elif type_of(value, dict):
        kvs = []
        for k in value:
            v = value[k]
            ks = "{}".format(to_lua(k))
            if ks.startswith("["):
                ks = "[ {} ]".format(ks)
            else:
                ks = "[{}]".format(ks)
            vs = to_lua(v)
            kvs.append("{} = {}".format(ks, vs))
        temp = "{{\n{}\n}}".format(indent(",\n".join(kvs), 1))
    elif type_of(value, list, tuple, set):
        kvs = []
        for i, v in enumerate(value):
            ks = "[{}]".format(i + 1)
            vs = to_lua(v)
            kvs.append("{} = {}".format(ks, vs))
        temp = "{{\n{}\n}}".format(indent(",\n".join(kvs), 1))
    else:
        temp = to_lua(str(value))

    return temp
