class Termination(Exception):
    """
    Superclass for all exceptions that signal a detection of properties or characteristics of a test that should end a
    test.
    """
    pass


class NotMovingTermination(Termination):
    """
    Signals that a test detected that an autonomous car does not move.
    """
    pass
