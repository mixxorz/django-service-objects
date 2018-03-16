from django import forms


class FooForm(forms.Form):
    name = forms.CharField(max_length=5)
