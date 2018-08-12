import abc
from contextlib import contextmanager

from django import forms
from django.db import transaction, DEFAULT_DB_ALIAS
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.models import ModelFormMetaclass
from django.utils import six

from .errors import InvalidInputsError


class ServiceMetaclass(abc.ABCMeta, DeclarativeFieldsMetaclass):
    pass


def get_initial_for_field_fill(klass, field, field_name):
            value = klass.initial.get(field_name, field.initial)
            if callable(value):
                value = value()
            return value


@six.add_metaclass(ServiceMetaclass)
class Service(forms.Form):
    """
    Based on Django's :class:`Form`, designed to encapsulate
    Business Rules functionality.  Input values are validated against
    the Service's defined fields before calling main functionality.
    """

    use_initials_as_default = False
    db_transaction = True
    using = DEFAULT_DB_ALIAS

    @classmethod
    def execute(cls, inputs, files=None, **kwargs):
        """
        Function to be called from the outside to kick off the Service
        functionality.

        :param dictionary inputs: data parameters for Service, checked
            against the fields defined on the Service class.

        :param dictionary files: usually request's FILES dictionary or
            None.

        :param dictionary kwargs: any additional parameters Service may
            need, can be an empty dictionary
        """
        instance = cls(inputs, files, **kwargs)
        instance.service_clean()
        with instance._process_context():
            return instance.process()

    def service_clean(self):
        """
        Calls base Form's :meth:`is_valid` to verify ``inputs`` against
        Service's fields and raises :class:`InvalidInputsError` if necessary.
        """
        if not self.is_valid():
            raise InvalidInputsError(self.errors, self.non_field_errors())

    def get_initial_for_field(self, field, field_name):
        """
        To make it work for django 1.8
        Get_initial_for_field_fill comes from django 2.0 codebase
        """
        try:
            return super(Service, self).get_initial_for_field(field, field_name)
        except AttributeError:
            return get_initial_for_field_fill(self, field, field_name)

    def full_clean(self):
        """
        Called before BaseForm.full_clean, use initial
        value as a fallback when no data is given.
        """
        if self.use_initials_as_default:
            for name, field in self.fields.items():
                if name not in self.data or not self.data[name]:
                    self.data[name] = self.get_initial_for_field(field, name)
        super(Service, self).full_clean()

    @abc.abstractmethod
    def process(self):
        """
        Main method to be overridden; contains the Business Rules
        functionality.
        """
        pass

    @contextmanager
    def _process_context(self):
        """
        Returns the context for :meth:`process`
        :return:
        """
        if self.db_transaction:
            with transaction.atomic(using=self.using):
                yield
        else:
            yield


class ModelServiceMetaclass(ServiceMetaclass, ModelFormMetaclass):
    pass


class ModelService(six.with_metaclass(ModelServiceMetaclass, Service)):
    """
    Same as :class:`Service` but auto-creates fields based on the provided
    :class:`Model`.  Additionally, You can manually create fields to override
    or extend the auto-created fields
    """
    pass
