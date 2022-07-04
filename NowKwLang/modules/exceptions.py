from NowKwLang.constants import MISSING

def raise_(exc: Exception = None, cause=MISSING):
    """
    throw an exception
    :param exc: the exception to raise
    :param cause: the cause of the exc
    :return: None
    """
    if exc is None:
        raise
    if cause is MISSING:
        raise exc
    else:
        raise exc from cause

raise_.__name__ = "raise"
