FAQ
===


How to specify the field that can store any value?
--------------------------------------------------

Use :class:`service_objects.fields.AnyField`:

.. code-block:: python
    :caption: your_app/services.py
    :name: service-example-py

    class YourService(Service):
        # payload can be any value except for: None, '', [], (), {}
        payload = AnyField()

Pass `empty_values` parameter if you want to ignore: None, '', [], (), {}.

.. code-block:: python
    :caption: your_app/services.py
    :name: service-example-py

    class YourService(Service):
        # payload can be any value including: None, '', [], (), {}
        payload = AnyField(empty_values=True)
