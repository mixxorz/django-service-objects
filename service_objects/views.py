from django.views.generic import FormView


class ServiceView(FormView):
    service_class = None

    def get_form_class(self):
        return self.form_class if self.form_class else self.service_class

    def get_service_class(self):
        return self.service_class

    def get_service_kwargs(self):
        return {}

    def get_service_input(self, form):
        return form.cleaned_data

    def get_service_files(self):
        rv = None
        if self.request.method in ('POST', 'PUT'):
            rv = self.request.FILES

        return rv

    def form_valid(self, form):
        try:
            cls = self.get_service_class()
            cls.execute(
                self.get_service_input(form),
                self.get_service_files(),
                **self.get_service_kwargs()
            )
            return super(ServiceView, self).form_valid(form)

        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
