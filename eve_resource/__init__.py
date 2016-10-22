# -*- coding: utf-8 -*-

from .exceptions import NotCallable, EveResourceError
from .hooks import Event, mongo_event, request_event, EventHooks, \
    mongo_hooks, request_hooks, Hooks
from .resource import Resource
from .utils import callable_or_error


__author__ = 'Michael Housh'
__email__ = 'mhoush@houshhomeenergy.com'
__version__ = '0.1.0'

__all__ = [
    # exceptions
    'NotCallable', 'EveResourceError',

    # hooks
    'Event', 'mongo_event', 'request_event', 'EventHooks', 'mongo_hooks',
    'request_hooks', 'Hooks',

    # resource
    'Resource',

    # utils
    'callable_or_error'

]
