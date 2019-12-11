from django import forms

from service_objects.fields import ModelField
from service_objects.celery_services import CeleryService
from service_objects.services import Service

from .models import CustomFooModel


class FooService(Service):
    bar = forms.CharField(required=True)


class MockService(Service):
    bar = forms.CharField(required=True)

    def process(self):
        pass


class NoDbTransactionService(Service):
    db_transaction = False

    def process(self):
        pass


class FooModelService(CeleryService):
    foo = ModelField(CustomFooModel)
    date = forms.DateField()
    text = forms.CharField()

    def process(self):
        pass
