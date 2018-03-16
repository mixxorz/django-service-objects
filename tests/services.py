from django import forms
from service_objects.services import Service


class FooService(Service):
    bar = forms.CharField(required=True)


class MockService(Service):
    bar = forms.CharField(required=True)


class NoDbTransactionService(Service):
    db_transaction = False
