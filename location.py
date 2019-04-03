from collections import namedtuple


class LocationError(Exception):
    pass


Location = namedtuple('Location', ['long', 'lat'])
