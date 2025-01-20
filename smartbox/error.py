class SmartboxError(Exception):
    """General errors from smartbox API"""

    pass


class SmartboxHomeNotFound(Exception):
    """We can't find this home"""

    pass
