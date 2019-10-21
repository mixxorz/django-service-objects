Usage
=====


Service
-------

Super easy. Just:

1. Create a new class that inherits from :class:`Service`
2. Add some fields, exactly like how you would with Django Forms
3. Define a :func:`process` method that contains your business logic

A code sample is worth a thousand words.

.. code-block:: python
    :caption: your_app/services.py
    :name: service-example-py

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
            self.booking = Booking.objects.create(
                customer=customer,
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                status=Booking.PENDING_VERIFICATION,
            )

            return self.booking

        def post_process(self):
            # Send verification email (check out django-herald)
            VerifyEmailNotification(self.booking).send()


Database transactions
+++++++++++++++++++++

By default, the process method on services runs inside a transaction. This is so
that if an exception is raised while executing your service, the database gets
rolled back to a clean state. If you don't want this behavior, you can set
``db_transaction = False`` on the service class.

.. code-block:: python
    :caption: your_app/services.py
    :name: service-no-transaction-py

    class NoDbTransactionService(Service):
        db_transaction = False


Function Based View
-------------------

.. code-block:: python
    :caption: your_app/views.py
    :name: fbv-view-example-py

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


Class Based View
----------------

.. code-block:: python
    :caption: your_app/views.py
    :name: cbv-view-example-py

    from django.core.urlresolvers import reverse_lazy

    from service_objects.views import ServiceView

    from .forms import BookingForm
    from .services import CreateBookingService


    class CreateBookingView(ServiceView):
        form_class = BookingForm
        service_class = CreateBookingService
        template_name = 'booking/create_booking.html'
        success_url = reverse_lazy('booking:success')


Testing
-------

An example of testing :class:`CreateBookingService`

.. code-block:: python
    :caption: your_app/tests.py
    :name: test-example-py

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
