import os

import django
from django.conf import settings
from django.core import management

BASE_DIR = os.path.dirname(__file__)
settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            }
        },
    LOCALE_PATHS=(
        os.path.join(BASE_DIR, 'locale'),
        ),

    )

django.setup()

management.call_command('compilemessages', verbosity=0,
                        interactive=False)
