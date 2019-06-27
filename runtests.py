import sys

import django
from django.conf import settings
from django.test.runner import DiscoverRunner

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test.db' if django.VERSION >= (2, 2) else ''
        }
    },
    INSTALLED_APPS=('tests',)
)
django.setup()

test_runner = DiscoverRunner(verbosity=1)
failures = test_runner.run_tests([])

if failures:
    sys.exit(failures)
