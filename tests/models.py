from django.db import models


class FooModel(models.Model):
    one = models.CharField(max_length=1)


class BarModel(models.Model):
    one = models.CharField(max_length=1)


class NonModel(object):
    pass
