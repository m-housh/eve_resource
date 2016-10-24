====
API
====

The public interface to ``EveResource``.

.. module:: eve_resource

Resource
--------

The following items are found in the ``eve_resource.resource`` module.

.. autoclass:: Resource
        :members:
        :noindex:


Hooks
-----

The following items are found in the ``eve_resource.hooks`` module.

.. autoclass:: Hooks
        :members:
        :noindex:

.. autoclass:: EventHooks
        :members:
        :noindex:

.. autofunction:: mongo_hooks

.. autofunction:: request_hooks


Events
------

The following item are found in the ``eve_resource.events`` module.

.. autoclass:: Event
        :members:
        :noindex:

.. autofunction:: mongo_event

.. autofunction:: request_event

Exceptions
----------

The following items are found in the ``eve_resource.exceptions`` module.

.. autoclass:: NotCallable
        :members:
        :noindex:

.. autoclass:: EveResourceError
        :members:
        :noindex:

Utils
-----

The following items are found in the ``eve_resource.utils`` mdoule.

.. autofunction:: callable_or_error

.. autofunction:: request_aliases

.. autofunction:: mongo_aliases
