from django import forms
from django.db import transaction

from .errors import InvalidInputsError


class Service(forms.Form):

    @classmethod
    def execute(cls, inputs, files=None, **kwargs):
        instance = cls(inputs, files, **kwargs)
        instance.service_clean()
        with transaction.atomic():
            return instance.process()

    def service_clean(self):
        if not self.is_valid():
            raise InvalidInputsError(self.errors, self.non_field_errors())

    def process(self):
        raise NotImplementedError()
