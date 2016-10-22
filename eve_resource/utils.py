# -*- coding: utf-8 -*-

from typing import Any, Callable

from .exceptions import NotCallable


def callable_or_error(func: Any) -> Callable[..., Any]:
    if not callable(func):
        raise NotCallable(func)
    return func
