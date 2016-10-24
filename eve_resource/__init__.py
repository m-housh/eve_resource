# -*- coding: utf-8 -*-

from .exceptions import NotCallable, EveResourceError
from .hooks import EventHooks, mongo_hooks, request_hooks, Hooks
from .event import Event, mongo_event, request_event
from .resource import Resource
from .utils import callable_or_error, request_aliases, mongo_aliases


__author__ = 'Michael Housh'
__email__ = 'mhoush@houshhomeenergy.com'
__version__ = '0.1.2'

__all__ = [
    # exceptions
    'NotCallable', 'EveResourceError',

    # hooks
    'EventHooks', 'mongo_hooks', 'request_hooks', 'Hooks',

    # events
    'Event', 'mongo_event', 'request_event',

    # resource
    'Resource',

    # utils
    'callable_or_error', 'mongo_aliases', 'request_aliases'

]
