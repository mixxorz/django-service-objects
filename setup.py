import os

from setuptools import find_packages, setup

import service_objects

BASE_DIR = os.path.dirname(__file__)
README_PATH = os.path.join(BASE_DIR, 'README.md')

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert(README_PATH, 'rst')
    LONG_DESCRIPTION_TYPE = 'text/x-rst; charset=UTF-8'
except (IOError, ImportError):
    LONG_DESCRIPTION_TYPE = 'text/markdown'
    if os.path.isfile(README_PATH):
        with open(README_PATH) as f:
            LONG_DESCRIPTION = f.read()
    else:
        LONG_DESCRIPTION = ''

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.path.pardir)))

setup(
    name='django-service-objects',
    version=service_objects.__version__,
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    license=service_objects.__license__,
    description=service_objects.__doc__,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    url='https://github.com/mixxorz/django-service-objects',
    author='Mitchel Cabuloy',
    author_email='mixxorz@gmail.com',
    maintainer='Mitchel Cabuloy',
    maintainer_email='mixxorz@gmail.com',
    install_requires=['Django>=1.11', 'six'],
    extras_require={'celery':  ['celery']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    test_suite='tests',
)
