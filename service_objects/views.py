from django.core.exceptions import ValidationError
from django.views.generic import FormView, UpdateView, CreateView
from six import viewitems

from .errors import InvalidInputsError


class ServiceViewMixin(object):
    service_class = None

    def get_form_class(self):
        """
        Overrides base class; returns :attr:`form_class` if defined,
        otherwise :attr:`service_class`.
        """
        return self.form_class if self.form_class else self.service_class

    def get_service_class(self):
        """
        Returns the class to use for :class:`Service` functionality.
        """
        return self.service_class

    def get_service_kwargs(self):
        """
        Returns a dictionary used as the ``**kwarg`` parameter on
        :class:`Service`.  By default, returns empty dictionary
        """
        return {}

    def get_service_input(self, form):
        """
        Returns a dictionary used as the ``input`` parameter on
        :class:`Service`.  By default, returns ``form``'s
        ``cleaned_data``
        """
        return form.cleaned_data

    def get_service_files(self):
        """
        If the current request is ``POST`` or ``PUT``, returns
        :attr:`request.FILES` otherwise ``None``
        """
        rv = None
        if self.request.method in ('POST', 'PUT'):
            rv = self.request.FILES

        return rv

    def form_valid(self, form):
        """
        Main functionality, creates :class:`Service` and calls
        :meth:`execute` with proper parameters.  If everything
        is successful, calls Base :meth:`form_valid`.  If error
        is throw, adds it to the form and calls :meth:`form_invalid`
        """
        try:
            cls = self.get_service_class()
            cls.execute(
                self.get_service_input(form),
                self.get_service_files(),
                **self.get_service_kwargs()
            )
            return super(ServiceViewMixin, self).form_valid(form)

        except InvalidInputsError as e:
            for k, v in viewitems(e.errors):
                form.add_error(k, v)
            return self.form_invalid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class ServiceView(ServiceViewMixin, FormView):
    """
    Based on Django's :class:`FormView`, designed to call a
    :class:`Service` class if the Form is valid.  If :attr:`form_class` is
    ``None``, ServiceView will use :attr:`service_class` for the Form to
    present the UI to the User::

        from django.core.urlresolvers import reverse_lazy

        from service_objects.views import ServiceView

        from .forms import BookingForm
        from .services import CreateBookingService


        class CreateBookingView(ServiceView):
            form_class = BookingForm
            service_class = CreateBookingService
            template_name = 'booking/create_booking.html'
            success_url = reverse_lazy('booking:success')

    """


class CreateServiceView(ServiceViewMixin, CreateView):
    """
    Based on Django's :class:`CreateView`, designed to call the
    :class:`Service` class if the form is valid.
    """


class UpdateServiceView(ServiceViewMixin, UpdateView):
    """
    Based on Django's :class:`UpdateView`, designed to call the
    :class:`Service` class if the form is valid.
    """
