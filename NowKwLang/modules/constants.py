
class EmptyValue:
    """
    Ellipsis, but falsy
    """
    def __new__(cls):
        return empty_value

    def __bool__(self):
        return False

    def __str__(self):
        return "..."

    def __eq__(self, other):
        return other is ... or other is self

    def __hash__(self):
        return hash(...)

empty_value = object.__new__(EmptyValue)
