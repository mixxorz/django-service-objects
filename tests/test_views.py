try:
    from unittest.mock import MagicMock, PropertyMock, patch, call
except ImportError:
    from mock import MagicMock, PropertyMock, patch, call

from unittest import TestCase

from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from service_objects.views import ServiceView
from service_objects.errors import InvalidInputsError


MockService = MagicMock()


MockForm = MagicMock()


class MockView(ServiceView):
    form_class = MockForm
    service_class = MockService


class FooView(ServiceView):
    service_class = MockService


class ExceptionServiceException(Exception):
    pass


ExceptionService = MagicMock()
ExceptionService.execute = MagicMock(side_effect=ExceptionServiceException('Testing'))

validation_error = ValidationError('Testing')

ValidationErrorService = MagicMock()
ValidationErrorService.execute = MagicMock(side_effect=validation_error)

field1_error = ValidationError('field1 Error')
non_field_error = ValidationError('nonfield Error')

invalid_inputs = InvalidInputsError(
    {
        NON_FIELD_ERRORS: [non_field_error,],
        'field1': [field1_error,],
    }, 
    {
        'field1': [field1_error,],
    }
)

InvalidInputsErrorService = MagicMock()
InvalidInputsErrorService.execute = MagicMock(side_effect=invalid_inputs)


class ExceptionView(ServiceView):
    service_class = ExceptionService


class ValidationErrorView(ServiceView):
    service_class = ValidationErrorService


class InvalidInputsErrorView(ServiceView):
    service_class = InvalidInputsErrorService


class ViewTest(TestCase):

    def build_request(self, method_return_value, FILES_return_value):
        request = MagicMock()
        method = PropertyMock(return_value=method_return_value)
        type(request).method = method
        FILES = PropertyMock(return_value=FILES_return_value)
        type(request).FILES = FILES

        return request, method, FILES

    def test_get_form_class(self):
        view = MockView()
        rv = view.get_form_class()

        self.assertEqual(MockForm, rv)

    def test_get_form_class_override(self):
        view = FooView()
        rv = view.get_form_class()

        self.assertEqual(MockService, rv)

    def test_get_service_class(self):
        view = MockView()
        rv = view.get_service_class()

        self.assertEqual(MockService, rv)

    def test_get_service_input(self):
        form = MagicMock()
        cleaned_data = PropertyMock(return_value={})
        type(form).cleaned_data = cleaned_data

        view = MockView()
        rv = view.get_service_input(form)

        cleaned_data.assert_called_once_with()
        self.assertEqual({}, rv)

    def test_get_service_files_none(self):
        request, method, FILES = self.build_request('GET', {})

        view = MockView()
        view.request = request
        rv = view.get_service_files()

        self.assertEqual(None, rv)
        method.assert_called_once_with()
        FILES.assert_not_called()

    def test_get_service_files_data(self):
        files = {'file1': 'filedata'}
        request, method, FILES = self.build_request('POST', files)

        view = MockView()
        view.request = request
        rv = view.get_service_files()

        self.assertEqual(files, rv)
        method.assert_called_once_with()
        FILES.assert_called_once_with()

    @patch('django.views.generic.FormView.form_valid')
    @patch('django.views.generic.FormView.form_invalid')
    def test_form_valid_exception(self, form_invalid, form_valid):
        request, _, _ = self.build_request('GET', {})
        form = MagicMock()

        view = ExceptionView()
        view.request = request

        with self.assertRaises(ExceptionServiceException):
            view.form_valid(form)

        form_valid.assert_not_called()
        form_invalid.assert_not_called()

    @patch('django.views.generic.FormView.form_valid')
    @patch('django.views.generic.FormView.form_invalid')
    def test_form_valid_validation_error(self, form_invalid, form_valid):
        request, _, _ = self.build_request('GET', {})
        form = MagicMock()

        view = ValidationErrorView()
        view.request = request
        view.form_valid(form)

        form_valid.assert_not_called()
        form_invalid.assert_called_once_with(form)
        form.add_error.assert_called_once_with(None, validation_error)

    @patch('django.views.generic.FormView.form_valid')
    @patch('django.views.generic.FormView.form_invalid')
    def test_form_valid_invalid_inputs_error(self, form_invalid, form_valid):
        request, _, _ = self.build_request('GET', {})
        form = MagicMock()

        view = InvalidInputsErrorView()
        view.request = request
        view.form_valid(form)

        form_valid.assert_not_called()
        form_invalid.assert_called_once_with(form)
        form.add_error.assert_has_calls([
            call(NON_FIELD_ERRORS, [non_field_error]),
            call('field1', [field1_error])
            ], any_order=True)

    @patch('django.views.generic.FormView.form_valid')
    @patch('django.views.generic.FormView.form_invalid')
    def test_form_valid_good(self, form_invalid, form_valid):
        request, _, _ = self.build_request('GET', {})
        form = MagicMock()

        view = MockView()
        view.request = request
        view.form_valid(form)

        form_valid.assert_called_once_with(form)
        form_invalid.assert_not_called()
