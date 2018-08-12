from django import forms

from service_objects.services import Service


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


def get_initial_data():
    return 'get_initial_data'


class InitialDataService(Service):
    bar = forms.CharField(required=False, initial='initial text')
    foo = forms.CharField(required=False)
    foobar = forms.CharField(required=False, initial=get_initial_data)
    use_initials_as_default = True

    def clean_bar(self):
        return self.cleaned_data['bar']

    def process(self):
        return self.cleaned_data


class InvalidInitialDataService(Service):
    bar = forms.IntegerField(required=False, initial='foo')
    use_initials_as_default = True

    def process(self):
        return self.cleaned_data
