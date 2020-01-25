from django.contrib import admin
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.core.exceptions import (
    PermissionDenied, NON_FIELD_ERRORS, ValidationError,
)
from django.forms import all_valid
from six import viewitems

from service_objects.errors import InvalidInputsError
from service_objects.views import ServiceViewMixin


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

    def _changeform_view(self, request, object_id, form_url, extra_context):
        if request.method != 'POST':
            return super(ModelAdminServiceView, self)._changeform_view(
                request, object_id, form_url, extra_context,
            )

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                "The field %s cannot be referenced." % to_field,
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
                    request, opts, object_id,
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
                    self.get_service_input(form),
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
