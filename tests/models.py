from django.db import models


class FooModel(models.Model):
    one = models.CharField(max_length=1)

