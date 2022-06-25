from NowKwLang.constants import MISSING

def raise_(exc: Exception = None, **kwargs):
    if exc is None:
        raise
    from_ = kwargs.pop("from", MISSING)
    if from_ is MISSING:
        raise exc
    else:
        raise exc from from_

raise_.__name__ = "raise"
