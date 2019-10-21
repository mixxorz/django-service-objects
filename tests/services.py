from django import forms

from service_objects.services import Service


class FooService(Service):
    bar = forms.CharField(required=True)


class MockService(Service):
    bar = forms.CharField(required=True)

    def process(self):
        pass

class MockCommitActionService(Service):
    has_on_commit_action = True

    bar = forms.CharField(required=True)

    def process(self):
        pass


class NoDbTransactionService(Service):
    db_transaction = False

    def process(self):
        pass
