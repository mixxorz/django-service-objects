"""Service objects for Django"""
from .errors import InvalidInputsError
from .fields import MultipleFormField, MultipleModelField, ModelField
from .services import Service, ModelService
from .views import ServiceView

__version__ = '0.4.0'
__license__ = 'MIT License'

__all__ = [
    'ModelService', 'MultipleFormField', 'MultipleModelField',
    'ModelField', 'InvalidInputsError', 'Service', 'ServiceView',
]
