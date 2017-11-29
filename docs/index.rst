.. Django Service Objects documentation master file, created by
   sphinx-quickstart on Thu Aug 24 08:09:47 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django Service Objects's documentation
======================================

What?
-----

This is a small library providing a :class:`Service` base class to derive your service objects from. What are service
objects? You can read more about the whys and hows in this
`blog post <http://mitchel.me/2017/django-service-objects/>`_, but for the most part, it encapsulates your business
logic, decoupling it from your views and model methods. Service objects are where your business logic should go.


Installation
------------

Like every other Python Package

``$ pip install django-service-objects``


.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   pages/philosophy
   pages/usage
   pages/faq
   pages/reference
   pages/support


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
