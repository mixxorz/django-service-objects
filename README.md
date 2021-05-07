# django-service-objects [![Latest Version][latest-version-image]][latest-version-link]
[![Build Status][build-status-image]][build-status-link]
[![Python Support][python-support-image]][python-support-link]
[![PyPI - Django Version][django-version-image]][django-link]
[![License][license-image]][license-link]

Service objects for Django

## What?

This is a small library providing a `Service` base class to derive your service objects from. What are service objects? You can read more about the whys and hows in [this blog post](http://mitchel.me/2017/django-service-objects/), but for the most part, it encapsulates your business logic, decoupling it from your views and model methods. Put your business logic in service objects.

## Installation guide

Install from pypi:

`pip install django-service-objects`

Add `service_objects` to your `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = (
    ...
    'service_objects',
    ...
)
```

## Example

Let's say you want to register new users. You could make a `CreateUser` service.

```python
from django import forms

from service_objects.services import Service

class CreateUser(Service):
    email = forms.EmailField()
    password = forms.CharField(max_length=255)
    subscribe_to_newsletter = forms.BooleanField(required=False)

    def process(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        subscribe_to_newsletter = self.cleaned_data['subscribe_to_newsletter']

        self.user = User.objects.create_user(username=email, email=email, password=password)
        self.subscribe_to_newsletter = subscribe_to_newsletter

        if self.subscribe_to_newsletter:
            newsletter = Newsletter.objects.get()
            newsletter.subscribers.add(self.user)
            newsletter.save()
            
        return self.user
    
    def post_process(self):
        WelcomeEmail.send(self.user, is_subscribed=self.subsribe_to_newsletter)
        
        # Calling a celery task after successfully creating the user.
        create_billing_account.delay(self.user.id)
```

Notice that it's basically a Django form but with a `process` method. This method gets called when you call `execute()` on the process. If your inputs are invalid, it raises `InvalidInputsError`.

The newly added `post_process` can also be included for running extra tasks that need to be executed after the service completes.

Here's how you use it:

```python
CreateUser.execute({
    'email': 'kvothe@edemaruh.com',
    'password': 'doorsofstone',
    'subscribe_to_newsletter': True,
})
```

Now you can use it anywhere.

In your views

```python
# views.py

# Function Based View
def create_user_view(request):
    form = NewUserForm()
    if request.method == 'POST':
        form = NewUserForm(request.POST)

        if form.is_valid():
            try:
                CreateUser.execute(request.POST)
                return redirect('/success/')
            except Exception:
                form.add_error(None, 'Something went wrong')

    return render(request, 'registration/new-user.html', {'form': form})


# Class Based View
class CreateUserView(ServiceView):
    form_class = NewUserForm
    service_class = CreateUser
    template_name = 'registration/new-user.html'
    success_url = '/success/'

```

A management command

```python
# management/commands/create_user.py

class Command(BaseCommand):
    help = "Creates a new user"

    def add_arguments(self, parser):
        parser.add_argument('email')
        parser.add_argument('password')

    def handle(self, *args, **options):
        user = CreateUser.execute(options)
        self.stdout.write(f'New user created : {user.email}')

```

In your tests

```python
class CreateUserTest(TestCase):

    def test_create_user(self):
        inputs = {
            'email': 'kvothe@edemaruh.com',
            'password': 'do0r$0f$stone42',
            'subscribe_to_newsletter': True,
        }

        CreateUser.execute(inputs)

        user = User.objects.get()
        self.assertEqual(user.email, inputs['email'])

        newsletter = Newsletter.objects.get()
        self.assertIn(user, newsletter.subscribers.all())
```

And anywhere you want. You can even execute services inside other services. The possibilities are endless!

## Documentation

Docs can be found on [readthedocs](http://django-service-objects.readthedocs.io/en/stable/).

If you have any questions about service objects, you can tweet me [@mixxorz](https://twitter.com/mixxorz).

[latest-version-image]: https://img.shields.io/pypi/v/django-service-objects.svg
[latest-version-link]: https://pypi.org/project/django-service-objects/
[build-status-image]: https://github.com/mixxorz/django-service-objects/workflows/Test/badge.svg
[build-status-link]: https://github.com/mixxorz/django-service-objects/actions
[python-support-image]: https://img.shields.io/pypi/pyversions/django-service-objects.svg
[python-support-link]: https://pypi.org/project/django-service-objects/
[django-version-image]: https://img.shields.io/pypi/djversions/django_service_objects.svg
[django-link]: https://docs.djangoproject.com/en/3.0/releases/
[license-image]: https://img.shields.io/pypi/l/django-service-objects.svg
[license-link]: https://github.com/mixxorz/django-service-objects/blob/master/LICENSE
