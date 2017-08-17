from django.db import models


class FooModel(models.Model):
    bar = models.CharField(max_length=5)

    class Meta:
        app_label = 'service_objects'