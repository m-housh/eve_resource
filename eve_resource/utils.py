# -*- coding: utf-8 -*-

from typing import Any, Callable, Dict

from .exceptions import NotCallable


def callable_or_error(func: Any) -> Callable[..., Any]:
    if not callable(func):
        raise NotCallable(func)
    return func


def mongo_aliases() -> Dict[str, str]:
    """Creates aliases for mongo events.

    """
    keys = ('fetch', 'insert', 'update', 'replace', 'delete')

    rv = {}  # type: AliasType
    for key in keys:
        rv[key] = 'on_' + key
        if key.endswith('e'):
            key = key + 'd'
        else:
            key = key + 'ed'

        rv[key] = 'on_' + key

    return rv


def request_aliases() -> Dict[str, str]:
    """Creates aliases for request events

    """
    keys = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')

    rv = {}  # type: AliasType
    for key in keys:
        rv['pre_' + key] = 'on_pre_' + key
        rv['post_' + key] = 'on_post_' + key

    return rv
