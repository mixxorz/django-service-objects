try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from unittest import TestCase

from django import forms

from service_objects.errors import InvalidInputsError
from service_objects.services import Service


class FooService(Service):
    bar = forms.CharField(required=True)


class MockService(Service):
    bar = forms.CharField(required=True)


MockService.process = Mock()


class ServiceTest(TestCase):

    def test_base_class(self):
        MockService.execute({'bar': 'Hello'})

        MockService.process.assert_called_with()

    def test_process_implemented(self):
        with self.assertRaises(NotImplementedError):
            FooService.execute({'bar': 'Hello'})

    def test_fields(self):
        with self.assertRaises(InvalidInputsError):
            MockService.execute({})

        MockService.execute({'bar': 'Hello'})

    def test_invalid_inputs_error(self):
        with self.assertRaises(InvalidInputsError) as cm:
            MockService.execute({})

        self.assertIn('InvalidInputsError', repr(cm.exception))
        self.assertIn('bar', repr(cm.exception))
        self.assertIn('This field is required.', repr(cm.exception))
