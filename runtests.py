import sys

import django
from django.conf import settings
from django.test.runner import DiscoverRunner

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    INSTALLED_APPS=('tests',),
    DEFAULT_AUTO_FIELD='django.db.models.AutoField',
)
django.setup()

test_runner = DiscoverRunner(verbosity=1)
failures = test_runner.run_tests([])

if failures:
    sys.exit(failures)
