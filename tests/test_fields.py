from unittest import TestCase

from django import forms
from django.core.exceptions import ValidationError

from service_objects.fields import MultipleFormField
from service_objects.models import FooModel


class FooForm(forms.Form):
    name = forms.CharField(max_length=5)


class FooModelForm(forms.ModelForm):
    class Meta:
        model = FooModel
        fields = ['bar']


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
        f = MultipleFormField(FooForm, min_count=1)

        with self.assertRaises(ValidationError) as cm:
            f.clean([])

        self.assertEqual(
            'There needs to be at least 1 item/s.', cm.exception.message)

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
            'There needs to be at most 2 item/s.', cm.exception.message)


class MultipleModelFormFieldTest(TestCase):
    def test_sanitation(self):
        f = MultipleFormField(FooModelForm)

        cleaned_data = f.clean([{
            'bar': 'abcde'
            }, {
            'bar': 'fghij'
            }])

        self.assertEqual(FooModelForm, type(cleaned_data[0]))
        self.assertEqual('abcde', cleaned_data[0].cleaned_data['bar'])

        self.assertEqual(FooModelForm, type(cleaned_data[1]))
        self.assertEqual('fghij', cleaned_data[1].cleaned_data['bar'])

    def test_sub_form_validation(self):
        f = MultipleFormField(FooModelForm)

        with self.assertRaises(ValidationError) as cm:
            f.clean([{'bar': ''}])

        self.assertIn('[0]', cm.exception.message)
        self.assertIn('bar', cm.exception.message)
        self.assertIn('This field is required.', cm.exception.message)

    def test_min_count(self):
        f = MultipleFormField(FooModelForm, min_count=1)

        with self.assertRaises(ValidationError) as cm:
            f.clean([])

        self.assertEqual(
            'There needs to be at least 1 item/s.', cm.exception.message)

    def test_max_count(self):
        f = MultipleFormField(FooModelForm, max_count=2)

        with self.assertRaises(ValidationError) as cm:
            f.clean([{
                'bar': 'abcde'
                }, {
                'bar': 'fghij'
                }, {
                'bar': 'klmno'
                }])

        self.assertEqual(
            'There needs to be at most 2 item/s.', cm.exception.message)

    def test_max_length(self):
        f = MultipleFormField(FooModelForm)

        with self.assertRaises(ValidationError) as cm:
            f.clean([{
                'bar': 'abcdea'
                }])

        self.assertIn('[0]', cm.exception.message)
        self.assertIn('bar', cm.exception.message)
        self.assertIn('Ensure this value has at most 5 characters', cm.exception.message)