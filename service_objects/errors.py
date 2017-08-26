class InvalidInputsError(Exception):
    """
    Raised during :class:`Service`'s :meth:`service_clean` method.
    Encapsulates both field_errors and non_field_errors into a single
    entity.

    :param dictionary errors: :class:`Services`'s ``errors`` dictionary

    :param dictionary non_field_errors: :class:`Service`'s
        ``non_field_errors`` dictionary
    """
    def __init__(self, errors, non_field_errors):
        self.errors = errors
        self.non_field_errors = non_field_errors

    def __repr__(self):
        return '{}({}, {})'.format(
            type(self).__name__, repr(self.errors), repr(self.non_field_errors))
