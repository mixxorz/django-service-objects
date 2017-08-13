class InvalidInputsError(Exception):

    def __init__(self, errors, non_field_errors):
        self.errors = errors
        self.non_field_errors = non_field_errors

    def __repr__(self):
        return '{}({}, {})'.format(
            type(self).__name__, repr(self.errors), repr(self.non_field_errors))
