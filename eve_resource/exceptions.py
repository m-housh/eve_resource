# -*- coding: utf-8 -*-


class EveResourceError(Exception):
    """The base exception class."""
    pass


class NotCallable(EveResourceError, TypeError):
    """Raised if an item is expected to be a callable, but is not."""

    def __init__(self, func) -> None:
        return super().__init__(
            '{} is not callable'.format(type(func))
        )
