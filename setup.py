from os import chdir
from os.path import abspath, dirname, join, normpath
from setuptools import find_packages, setup

import service_objects

pypi_readme = """
django-service-objects
======================

Service objects for Django

`Go to GitHub for more info <https://github.com/mixxorz/django-service-objects>`_
"""  # noqa


def read_file(filename):
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


# allow setup.py to be run from any path
chdir(normpath(abspath(dirname(__file__))))

setup(
    name='django-service-objects',
    version=service_objects.__version__,
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    license=service_objects.__license__,
    description=service_objects.__doc__,
    long_description=pypi_readme,
    url='https://github.com/mixxorz/django-service-objects',
    author='Mitchel Cabuloy',
    author_email='mixxorz@gmail.com',
    maintainer='Mitchel Cabuloy',
    maintainer_email='mixxorz@gmail.com',
    install_requires=['Django>=1.8', 'six'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    test_suite='tests',
)
