from django import forms
from django.core.exceptions import ValidationError


class MultipleFormField(forms.Field):
    """
    A field for :class:`Service` that accepts a list of objects which is
    translated into multiple :class:`Form` objects::

        class PersonForm(forms.Form):
            name = forms.CharField()


        class UpdateOrganizationService(Service):
            people = MultipleFormField(PersonForm)

            def process(self):
                people = self.cleaned_data['people']
                for person in people:
                    print(person.cleaned_data['name'])

        UpdateOrganizationService.execute({
            'people': [
                { 'name': 'John Smith' },
                { 'name': 'Adam Davis' },
            ]
        })
    """

    def __init__(self, form_class, min_count=1, max_count=None, *args,
                 **kwargs):
        super(MultipleFormField, self).__init__(*args, **kwargs)

        self.form_class = form_class
        self.min_count = min_count
        self.max_count = max_count

    def clean(self, values):
        if len(values) < self.min_count:
            raise ValidationError(
                'There needs to be at least {} item/s.'.format(self.min_count))

        if self.max_count and len(values) > self.max_count:
            raise ValidationError(
                'There needs to be at most {} item/s.'.format(self.max_count))

        item_forms = []
        for index, item in enumerate(values):
            item_form = self.form_class(item)
            if not item_form.is_valid():
                raise ValidationError(
                    '[{}]: {}'.format(index, repr(item_form.errors)))
            item_forms.append(item_form)

        return item_forms
