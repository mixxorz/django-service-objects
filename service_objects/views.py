import django
from django.contrib import admin
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied, NON_FIELD_ERRORS
from django.core.exceptions import ValidationError
from django.db import transaction, router
from django.forms import all_valid
from django.utils.decorators import method_decorator
from django.utils.six import viewitems
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, UpdateView, CreateView

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


class ModelAdminServiceView(ServiceViewMixin, admin.ModelAdmin):
    """
    Based on Django's :class:`django.contrib.admin.ModelAdmin` calls the
    :class:`Service` if the form is valid.
    """

    def get_service_files(self, request=None):
        """
        If the current request is ``POST`` or ``PUT``, returns
        :attr:`request.FILES` otherwise ``None``
        """
        if request and request.method in ('POST', 'PUT'):
            return request.FILES

    def get_service_kwargs(self):
        """
        Returns a dictionary used as the `**kwarg` parameter
        on :class:`Service`.
        By default, returns a dictionary with commit=False
        """
        return {'commit': False}

    @method_decorator(csrf_protect)
    def changeform_view(self, request, object_id=None, form_url='',
                        extra_context=None):
        # Currently supported by Django>=1.11,>=2.0
        if django.VERSION >= (1, 11):
            with transaction.atomic(using=router.db_for_write(self.model)):
                return self._changeform_view(
                   request, object_id, form_url, extra_context,
                )
        return (
            super(ModelAdminServiceView, self).changeform_view(
                request, object_id=None, form_url='', extra_context=None,
            )
        )

    def _changeform_view(self, request, object_id, form_url, extra_context):
        if request.method != 'POST':
            return super(ModelAdminServiceView, self)._changeform_view(
                request, object_id, form_url, extra_context,
            )

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                "The field %s cannot be referenced." % to_field
            )

        model = self.model
        opts = model._meta

        if request.method == 'POST' and '_saveasnew' in request.POST:
            object_id = None

        add = object_id is None

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None
        else:
            obj = self.get_object(request, unquote(object_id), to_field)

            if not self.has_change_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(
                    request, opts, object_id
                )

        ModelForm = self.get_form(request, obj)

        form = ModelForm(request.POST, request.FILES, instance=obj)
        form_validated = service_validated = False
        service_ret_form = None

        if form.is_valid():
            form_validated = True
            try:
                cls = self.get_service_class()
                service_ret_form = cls.execute(
                    data=self.get_service_input(form),
                    files=self.get_service_files(request),
                    **self.get_service_kwargs()
                )
            except InvalidInputsError as e:
                for k, v in viewitems(e.errors):
                    form.add_error(k, v)
            except ValidationError as e:
                form.add_error(NON_FIELD_ERRORS, e)
            else:
                service_validated = True

        if form_validated and service_validated:
            form = service_ret_form
            new_object = service_ret_form.instance
        else:
            form_validated = False
            new_object = form.instance
        formsets, inline_instances = self._create_formsets(
            request, new_object, change=not add,
        )
        if all_valid(formsets) and form_validated:
            self.save_model(request, new_object, form, not add)
            self.save_related(request, form, formsets, not add)
            change_message = self.construct_change_message(
                request, form, formsets, add,
            )
            if add:
                self.log_addition(request, new_object, change_message)
                return self.response_add(request, new_object)
            else:
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        return (
            super(ModelAdminServiceView, self)._changeform_view(
                request, object_id, form_url, extra_context,
            )
        )
