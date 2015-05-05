import Pyro4


def proxy(uri):
    light = Pyro4.Proxy(uri)
    return light
