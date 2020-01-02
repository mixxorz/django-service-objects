from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import ungettext_lazy, gettext_lazy as _


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
    error_min = ungettext_lazy("There needs to be at least %(num)d item.",
                               "There needs to be at least %(num)d items.",
                               'num')
    error_max = ungettext_lazy("There needs to be at most %(num)d item.",
                               "There needs to be at most %(num)d items.",
                               'num')
    error_required = _("Input is required. "
                       "Expected not empty list but got %(values)r.")

    def __init__(self, form_class, min_count=1, max_count=None, *args,
                 **kwargs):
        super(MultipleFormField, self).__init__(*args, **kwargs)

        self.form_class = form_class
        self.min_count = min_count
        self.max_count = max_count

    def clean(self, values):
        if not values and values is not False:
            if self.required:
                raise ValidationError(self.error_required % {
                    'values': values
                })
            else:
                return []

        if len(values) < self.min_count:
            raise ValidationError(self.error_min % {'num': self.min_count})

        if self.max_count and len(values) > self.max_count:
            raise ValidationError(self.error_max % {'num': self.max_count})

        item_forms = []
        for index, item in enumerate(values):
            item_form = self.form_class(item)
            if not item_form.is_valid():
                raise ValidationError(
                    '[{}]: {}'.format(index, repr(item_form.errors)))
            item_forms.append(item_form)

        return item_forms


class ModelField(forms.Field):
    """
    A field for :class:`Service` that accepts an object of the specified
    :class:`Model`::

        class Person(models.Model):
            first_name = models.CharField(max_length=30)
            last_name = models.CharField(max_length=30)
            last_updated = models.DateTimeField()


        class UpdatePerson(Service):
            person = ModelField(Person)

            process(self):
                person = self.cleaned_data['person']
                person.last_updated = now()
                person.save()


        user = Person(first_name='John', last_name='Smith')
        user.save()

        UpdatePerson.execute({
            'person': user
        })


    :param model_class: Django :class:`Model` or dotted string of :
            class:`Model` name
    :param allow_unsaved: Whether the object is required to be saved to
            the database
    """
    error_model_class = _("%(cls_name)s(%(model_class)r) is invalid.  First "
                          "parameter of ModelField must be either a model or a "
                          "model name.")
    error_type = _("Objects needs to be of type %(model_class)r")
    error_unsaved = _("Unsaved objects are not allowed.")
    error_required = _("Input is required. Expected model but got %(value)r.")

    def __init__(self, model_class, allow_unsaved=False, *args, **kwargs):
        super(ModelField, self).__init__(*args, **kwargs)

        try:
            model_class._meta.model_name
        except AttributeError:
            assert isinstance(model_class, str), self.error_model_class % {
                'cls_name': self.__class__.__name__,
                'model_class': model_class
            }

        self.model_class = model_class
        if isinstance(model_class, str):
            label = model_class.split('.')
            app_label = ".".join(label[:-1])
            model_name = label[-1]
            self.model_class = apps.get_model(app_label, model_name)

        self.allow_unsaved = allow_unsaved

    def clean(self, value):
        if not value and value is not False:
            if self.required:
                raise ValidationError(self.error_required % {
                    'value': value
                })
        else:
            self.check_type(value)
            self.check_unsaved(value)
        return value

    def check_type(self, item):
        if not isinstance(item, self.model_class):
            raise ValidationError(self.error_type % {
                'model_class': self.model_class
                }
            )

    def check_unsaved(self, item):
        if (self.allow_unsaved is False and item.pk is None):
            raise ValidationError(self.error_unsaved)


class MultipleModelField(ModelField):
    """
    A multiple model version of :class:`ModelField`, will check each passed
    in object to match the specified :class:`Model`::

        class Person(models.Model):
            first_name = models.CharField(max_length=30)
            last_name = models.CharField(max_length=30)


        class AssociatePeople(Service):
            people = MultipleModelField(Person, allow_unsaved=True)


        users = [
            Person(first_name='John', last_name='Smith'),
            Person(first_name='Jane', last_name='Smith')
        ]

        AssociatePeople.execute({
            'people': users
        })

        for user in users:
            user.save()

    :param model_class: Django :class:`Model` or dotted string of :
            class:`Model` name
    :param allow_unsaved: Whether the object is required to be saved to
            the database

    """
    error_non_iterable = _("Object is not iterable.")
    error_required = _("Input is required expected list "
                       "of models but got %(values)r.")

    def clean(self, values):
        if not values and values is not False:
            if self.required:
                raise ValidationError(self.error_required % {
                    'values': values
                })
            else:
                return values

        try:
            _ = iter(values)
        except TypeError:
            raise ValidationError(self.error_non_iterable)

        for value in values:
            self.check_type(value)
            self.check_unsaved(value)
        return values
