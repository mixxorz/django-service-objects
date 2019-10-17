import datetime
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
import pickle

from django.test import TestCase

from service_objects.celery_services import celery_service_task, CeleryService

from tests.models import CustomFooModel
from tests.services import FooModelService


class CeleryServiceTest(TestCase):
    def setUp(self):
        self.foo = CustomFooModel.objects.create(
            custom_pk=f"custom-{id(self)}", one="custom"
        )
        self.initial_data = {
            "foo": self.foo,
            "date": datetime.date.today(),
            "text": "text",
        }

    def test_cleaned_data_pickling(self):
        service = FooModelService(self.initial_data)
        service.is_valid()

        # Check deflated ModelField format
        self.assertEqual(
            CeleryService._deflate_models(service.cleaned_data),
            {**self.initial_data, "foo": (CustomFooModel, self.foo.pk)},
        )

        # Check deflate/inflate invariant
        self.assertEqual(
            CeleryService._inflate_models(
                CeleryService._deflate_models(service.cleaned_data)
            ),
            service.cleaned_data,
        )

        # Check deflated data picklable invariant
        deflated_data = CeleryService._deflate_models(service.cleaned_data)
        self.assertEqual(pickle.loads(pickle.dumps(deflated_data)), deflated_data)

    def test_form_data_reaching_executor(self):

        celery_task_dispatched = False
        cleaned_data = None

        def apply_sync(*args, **kwargs):
            nonlocal celery_task_dispatched
            celery_task_dispatched = True
            return celery_service_task.apply(*args, **kwargs)

        def process(_self):
            nonlocal cleaned_data
            cleaned_data = _self.cleaned_data

        with patch(
            "service_objects.celery_services.celery_service_task.apply_async", apply_sync
        ):

            with patch("tests.test_services.FooModelService.process", process):

                FooModelService.execute(self.initial_data)
                self.assertTrue(celery_task_dispatched)
                self.assertEqual(cleaned_data, self.initial_data)
