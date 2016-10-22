# -*- coding: utf-8 -*-

from typing import Optional, Callable, Any, Dict, Tuple
from collections import namedtuple

from eve import Eve

from . import hooks
from . import utils


OptionalFunc = Optional[Callable[..., Any]]


class Resource(object):

    def __init__(self, name, *keys):
        self.name = name
        self._key = None  # type: namedtuple
        self._definition = None
        self._schema = None
        self.hooks = hooks.Hooks(self.name)

        if len(keys) > 0:
            self.keys(*keys)

    @property
    def key(self) -> Optional[Tuple]:
        return self._key

    def keys(self, *keys):
        Key = namedtuple('Key', keys)
        self._key = Key(*keys)

    def _validate_func(self, func: OptionalFunc, callback: OptionalFunc=None
                       ) -> Any:

        func = utils.callable_or_error(func)
        return callback(func) if callback is not None else func

    def set_definition(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise TypeError(data)

        self._definition = data

    def definition(self, func: OptionalFunc=None) -> None:

        def callback(func):
            self.set_definition(func())

        if func is not None:
            return self._validate_func(func, callback)
        return self._definition

    def set_schema(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise TypeError(data)

        self._schema = data

    def schema(self, func: OptionalFunc=None) -> None:

        def callback(func):
            try:
                self.set_schema(func(self.key))
            except TypeError:
                self.set_schema(func())

        if func is not None:
            return self._validate_func(func, callback)
        return self._schema

    def domain(self) -> Dict[str, Any]:
        if self.definition() is None:
            domain = {}
        else:
            domain = self.definition().copy()

        domain.setdefault('schema', self.schema())
        return domain

    def init_api(self, api: Eve) -> None:
        """Register's the event hooks with the api and also will register
        the domain with the api, if one does not exist for the resource.

        :param api:  An :class:`eve.Eve` instance.

        :raises TypeError:  If api is not an :class:`eve.Eve` instance.

        """
        if not isinstance(api, Eve):
            raise TypeError(api)
        # add event hooks to the api
        self.hooks.init_api(api)
        # register the domain with the api.
        api.config['DOMAIN'].setdefault(self.name, self.domain())
