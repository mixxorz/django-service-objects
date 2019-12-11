from celery import shared_task

from django.db import models

from .services import Service


@shared_task
def celery_service_task(cleaned_data, service_class=None):
    """
    Task for dispatching `CeleryService`s execution to
    """
    service_class._inflate_and_execute(cleaned_data)


class CeleryService(Service):
    @staticmethod
    def _deflate_model(value):
        """
        Transforms model instances into picklable tuple.
        """
        if isinstance(value, models.Model):
            return (value.__class__, value.pk)
        return value

    @staticmethod
    def _inflate_model(value):
        """
        Inflate picklable tuple (of model-class and pk)- back to model instance.
        """
        if isinstance(value, tuple) and len(value) == 2:
            model_class, pk = value
            if isinstance(model_class, type) and issubclass(
                model_class, models.Model
            ):  # noqa
                return model_class.objects.get(pk=pk)
        return value

    @classmethod
    def _deflate_models(cls, cleaned_data):
        return {
            key: cls._deflate_model(value)
            for key, value in cleaned_data.items()  # noqa
        }

    @classmethod
    def _inflate_models(cls, cleaned_data):
        return {
            key: cls._inflate_model(value)
            for key, value in cleaned_data.items()  # noqa
        }

    @classmethod
    def _inflate_and_execute(cls, cleaned_data):
        instance = cls({})
        cleaned_data = cls._inflate_models(cleaned_data)
        setattr(instance, "cleaned_data", cleaned_data)

        with instance._process_context():
            return instance.process()

    @classmethod
    def execute(cls, inputs, files=None, sync=False, **kwargs):
        """
        Dispatches service excecution to the celery task.

        :param dictionary inputs: data parameters for Service,
            checked against the fields defined on the Service class.

        :param dictionary files: usually request's FILES dictionary
            or None.

        :param bool sync: executes as a normal `Service` if `True`
            (default `False`).

        :param dictionary kwargs: any extra parameters You want pass
            to celery task.
        """
        instance = cls(inputs, files, **kwargs)
        instance.service_clean()

        if sync:
            with instance._process_context():
                return instance.process()
        else:
            cleaned_data = cls._deflate_models(instance.cleaned_data)
            celery_service_task.apply_async(
                args=(cleaned_data,),
                kwargs={"service_class": cls},
                serializer="pickle",
                **kwargs
            )
