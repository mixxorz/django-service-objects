# django-service-objects [![Latest Version][latest-version-image]][latest-version-link]
[![Build Status][build-status-image]][build-status-link] [![Python Support][python-support-image]][python-support-link] [![License][license-image]][license-link]

Service objects for Django

## What?

This is a small library providing a `Service` base class to derive your service objects from. What are service objects? You can read more about the whys and hows in [my blog post](http://mitchel.me/2017/django-service-objects/), but for the most part, it encapsulates your business logic, decoupling it from your views and model methods. Service objects are where your business logic should go.

## Installation

Like every other Python package

```
$ pip install django-service-objects
```

## Usage

Super easy. Just:

1. Create a new class that inherits from `Service`
2. Add some fields, exactly like how you would with Django Forms
3. Define a `process` method that contains your business logic

A code sample is worth a thousand words.

```python
# your_app/services.py

from django import forms
from service_objects.services import Service

from .models import Booking, Customer
from .notifications import VerifyEmailNotification


class CreateBookingService(Service):
    name = forms.CharField()
    email = forms.EmailField()
    checkin_date = forms.DateField()
    checkout_date = forms.DateField()

    def process(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        checkin_date = self.cleaned_data['checkin_date']
        checkout_date = self.cleaned_data['checkout_date']

        # Update or create a customer
        customer = Customer.objects.update_or_create(
            email=email,
            defaults={
                'name': name
            }
        )

        # Create booking
        booking = Booking.objects.create(
            customer=customer,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            status=Booking.PENDING_VERIFICATION,
        )

        # Send verification email (check out django-herald)
        VerifyEmailNotification(booking).send()

        return booking
```

You can use this service object anywhere. Here's an example of it being used in a regular Django view:

```python
# your_app/views.py

from django.shortcuts import redirect, render

from .forms import BookingForm
from .services import CreateBookingService

def create_booking_view(request):
    form = BookingForm()

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
              # Services raise InvalidInputsError if you pass
              # invalid values into it.
              CreateBookingService.execute({
                  'name': form.cleaned_data['name'],
                  'email': form.cleaned_data['email'],
                  'checkin_date': form.cleaned_data['checkin_date'],
                  'checkout_date': form.cleaned_data['checkout_date'],
              })
              return redirect('booking:success')
            except Exception as e:
                form.add_error(None, f'Sorry. Something went wrong: {e}')

    return render(request, 'booking/create_booking.html', {'form': form})
```

An example of testing CreateBookingService

```python
# your_app/tests.py
from datetime import date

from django.core import mail
from django.test import TestCase

from .models import Booking, Customer
from .services import CreateBookingService


class CreateBookingServiceTest(TestCase):

    def test_create_booking(self):
        inputs = {
            'name': 'John Doe',
            'email': 'john@doe.com',
            'checkin_date': date(2017, 8, 13),
            'checkout_date': date(2017, 8, 15),
        }

        booking = CreateBookingService.execute(inputs)

        # Test that a Customer gets created
        customer = Customer.objects.get()
        self.assertEqual(customer.name, inputs['name'])
        self.assertEqual(customer.email, inputs['email'])

        # Test that a Booking gets created
        booking = Booking.objects.get()

        self.assertEqual(customer, booking.customer)
        self.assertEqual(booking.checkin_date, inputs['checkin_date'])
        self.assertEqual(booking.checkout_date, inputs['checkout_date'])

        # Test that the verification email gets sent
        self.assertEqual(1, len(mail.outbox))

        email = mail.outbox[0]
        self.assertIn('verify email address', email.body)
```

## Support

Tests are run on officially supported versions of Django

* Python 2.7, 3.4, 3.5, 3.6
* Django 1.8, 1.10, 1.11

[latest-version-image]: https://img.shields.io/pypi/v/django-service-objects.svg
[latest-version-link]: https://pypi.python.org/pypi/django-service-objects/
[build-status-image]: https://img.shields.io/travis/mixxorz/django-service-objects/master.svg
[build-status-link]: https://travis-ci.org/mixxorz/django-service-objects
[python-support-image]: https://img.shields.io/pypi/pyversions/django-service-objects.svg
[python-support-link]: https://pypi.python.org/pypi/django-service-objects
[license-image]: https://img.shields.io/pypi/l/django-service-objects.svg
[license-link]: https://github.com/mixxorz/django-service-objects/blob/master/LICENSE
