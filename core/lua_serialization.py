# https://gist.github.com/SegFaultAX/629a3a8c15b0fd188000

def type_of(v, *types):
    return any(isinstance(v, t) for t in types)


def to_lua(value):
    if type_of(value, str):
        temp = "\"%s\"" % value.replace("\"", "\\\"")
    elif type_of(value, float, int):
        temp = "{}".format(value)
    elif type_of(value, dict):
        kvs = []
        for k in value:
            v = value[k]
            ks = "{}".format(to_lua(k))
            if ks.startswith("["):
                ks = "[{}]".format(ks)
            else:
                ks = "[{}]".format(ks)
            vs = to_lua(v)
            kvs.append("{}={}".format(ks, vs))
        temp = "{{{}}}".format(",".join(kvs))
    elif type_of(value, list, tuple, set):
        kvs = []
        for i, v in enumerate(value):
            ks = "[{}]".format(i + 1)
            vs = to_lua(v)
            kvs.append("{}={}".format(ks, vs))
        temp = "{{{}}}".format(",".join(kvs))
    else:
        raise ValueError

    return temp
