Philosophy
==========


Decoupled from presentation logic
---------------------------------

Now that your business logic is in its own class, you can call it from anywhere. From regular Django views, JSON
endpoints, management commands, RQ tasks, Django admin, etc. Your business logic is no longer bound to your views
or models.


Easily testable and mockable
----------------------------

Since service objects are just objects, you can easily call them from your tests to verify their behavior. Similarly,
if you’re testing your view or endpoint, you can easily mock out the service objects.


Input validation
----------------

Your code will become a lot more concise now that you don’t have to manually check whether or not a parameter is valid.
If you need to know why your inputs failed validation, just catch :class:`InvalidInputsError` and access the
:attr:`errors` or :attr:`non_field_errors` dictionary. Better yet, raise a custom exception from your service object.


But fat models…
---------------

Models just ended up doing too many things. Plus it wasn’t very clear which model a method belongs to if it operated on
two different models. (Should :class:`Booking` have :func:`create_booking` or should :class:`Customer`)?
