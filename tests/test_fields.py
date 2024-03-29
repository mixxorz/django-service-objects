from unittest import TestCase

from django.core.exceptions import ValidationError

from service_objects.fields import MultipleFormField, ModelField, MultipleModelField, \
    DictField, ListField
from tests.forms import FooForm
from tests.models import FooModel, BarModel, NonModel


class MultipleFormFieldTest(TestCase):

    def test_sanitation(self):
        f = MultipleFormField(FooForm)

        cleaned_data = f.clean([{
            'name': 'abcde'
        }, {
            'name': 'fghij'
        }])

        self.assertEqual(FooForm, type(cleaned_data[0]))
        self.assertEqual('abcde', cleaned_data[0].cleaned_data['name'])

        self.assertEqual(FooForm, type(cleaned_data[1]))
        self.assertEqual('fghij', cleaned_data[1].cleaned_data['name'])

    def test_sub_form_validation(self):
        f = MultipleFormField(FooForm)

        with self.assertRaises(ValidationError) as cm:
            f.clean([{'name': ''}])

        self.assertIn('[0]', cm.exception.message)
        self.assertIn('name', cm.exception.message)
        self.assertIn('This field is required.', cm.exception.message)

    def test_min_count(self):
        f = MultipleFormField(FooForm, min_count=2)

        with self.assertRaises(ValidationError) as cm:
            f.clean(['1'])

        self.assertEqual(
            'There needs to be at least 2 items.', cm.exception.message)

    def test_max_count(self):
        f = MultipleFormField(FooForm, max_count=2)

        with self.assertRaises(ValidationError) as cm:
            f.clean([{
                'name': 'abcde'
            }, {
                'name': 'fghij'
            }, {
                'name': 'klmno'
            }])

        self.assertEqual(
            'There needs to be at most 2 items.', cm.exception.message)

    def test_is_requred(self):
        f = MultipleFormField(FooForm)
        with self.assertRaises(ValidationError) as cm:
            f.clean([])

        self.assertEqual(
            'Input is required. Expected not empty list but got [].', cm.exception.message)

    def test_is_not_requred(self):
        f = MultipleFormField(FooForm, required=False)
        # should not raise any exception
        f.clean(None)
        f.clean([])


class ModelFieldTest(TestCase):

    def test_init_model_class_invalid(self):
        with self.assertRaisesRegexp(AssertionError, "NonModel"):
            rv = ModelField(NonModel)

    def test_init_model_class_valid(self):
        rv = ModelField(FooModel)

        self.assertEqual(FooModel, rv.model_class)

    def test_init_model_class_string(self):
        rv = ModelField('tests.BarModel')

        self.assertEqual(BarModel, rv.model_class)

    def test_model_invalid_type(self):
        model_field = ModelField(FooModel)
        model = BarModel(one='Z')

        with self.assertRaisesRegexp(ValidationError, "FooModel"):
            cleaned_data = model_field.clean(model)

    def test_model_valid_type(self):
        model_field = ModelField(FooModel)
        model = FooModel(one='Z')
        model.pk = 1

        cleaned_data = model_field.clean(model)

        self.assertTrue(model, cleaned_data)

    def test_allow_unsaved_false(self):
        model_field = ModelField(FooModel)
        model = FooModel(one='Z')

        with self.assertRaisesRegexp(ValidationError, "[Uu]nsaved"):
            cleaned_data = model_field.clean(model)

    def test_allow_unsaved_true(self):
        model_field = ModelField(FooModel, allow_unsaved=True)
        model = FooModel(one='Z')

        cleaned_data = model_field.clean(model)

        self.assertTrue(model, cleaned_data)

    def test_is_requred(self):
        f = ModelField(FooModel)
        with self.assertRaises(ValidationError) as cm:
            f.clean(None)

        self.assertEqual(
            'Input is required. Expected model but got None.', cm.exception.message)

    def test_is_not_requred(self):
        f = ModelField(FooModel, required=False)
        # should not raise any exception
        f.clean(None)


class MultipleModelFieldTest(TestCase):

    def test_multiple_invalid_type(self):
        model_field = MultipleModelField(FooModel, allow_unsaved=True)
        objects = [
            FooModel(one='a'),
            FooModel(one='b'),
            BarModel(one='c')
        ]

        with self.assertRaisesRegexp(ValidationError, "FooModel"):
            cleaned_data = model_field.clean(objects)

    def test_multiple_unsaved_false(self):
        model_field = MultipleModelField(FooModel)
        objects = [
            FooModel(one='a'),
            FooModel(one='b')
        ]
        for obj in objects:
            obj.pk = 1
        objects.append(FooModel(one='c'))

        with self.assertRaisesRegexp(ValidationError, "[Uu]nsaved"):
            cleaned_data = model_field.clean(objects)

    def test_multiple_non_list(self):
        model_field = MultipleModelField(FooModel)
        obj = FooModel(one='a')
        obj.pk = 1

        with self.assertRaisesRegexp(ValidationError, "[Ii]terable"):
            cleaned_data = model_field.clean(obj)

    def test_multiple_valid(self):
        model_field = MultipleModelField(FooModel)
        objects = [
            FooModel(one='a'),
            FooModel(one='b')
        ]
        for obj in objects:
            obj.pk = 1

        cleaned_data = model_field.clean(objects)

        self.assertEqual(objects, cleaned_data)

    def test_is_required(self):
        f = MultipleModelField(FooModel)
        with self.assertRaises(ValidationError) as cm:
            f.clean(None)

        self.assertEqual(
            'Input is required expected list of models but got None.', cm.exception.message)

    def test_is_not_required(self):
        f = MultipleModelField(FooModel, required=False)
        # should not raise any exception
        f.clean(None)


class DictFieldTest(TestCase):
    def test_is_required(self):
        dict_field = DictField(required=True)

        with self.assertRaises(ValidationError) as cm:
            dict_field.clean(None)

        self.assertEqual(
            'Input is required. Expected dict but got None.', cm.exception.message)

    def test_is_not_required(self):
        dict_field = DictField(required=False)

        # should not raise any exception
        dict_field.clean(None)

    def test_invalid_type(self):
        dict_field = DictField(required=True)

        with self.assertRaises(ValidationError) as cm:
            dict_field.clean('string test')

        self.assertEqual(
            'Input needs to be of type dict.', cm.exception.message)

    def test_validators(self):
        def has_foo_key(my_dict):
            if "foo" not in my_dict:
                raise ValidationError("dict must have `foo` key")

        list_field = DictField(validators=[has_foo_key])

        with self.assertRaises(ValidationError) as cm:
            list_field.clean({"bar": "baz"})

        self.assertEqual(["dict must have `foo` key"], cm.exception.messages)


class ListFieldTest(TestCase):
    def test_is_required(self):
        list_field = ListField(required=True)

        with self.assertRaises(ValidationError) as cm:
            list_field.clean(None)

        self.assertEqual(
            'Input is required. Expected list but got None.', cm.exception.message)

    def test_is_not_required(self):
        list_field = ListField(required=False)

        # should not raise any exception
        list_field.clean(None)

    def test_invalid_type(self):
        list_field = ListField(required=True)

        with self.assertRaises(ValidationError) as cm:
            list_field.clean('string test')

        self.assertEqual(
            'Input needs to be of type list.', cm.exception.message)

    def test_validators(self):
        def starts_with_a(values):
            for value in values:
                if not value.startswith("a"):
                    raise ValidationError(f"'{value}' must start with a")

        list_field = ListField(validators=[starts_with_a])

        with self.assertRaises(ValidationError) as cm:
            list_field.clean(['a valid string', 'invalid string'])

        self.assertEqual(["'invalid string' must start with a"], cm.exception.messages)
