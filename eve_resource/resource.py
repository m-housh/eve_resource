# -*- coding: utf-8 -*-

from typing import Optional, Callable, Any, Dict, NamedTuple
from collections import namedtuple

from eve import Eve

from . import hooks
from . import utils


OptionalFunc = Optional[Callable[..., Any]]


class Resource(object):
    """A domain resource for :class:`eve.Eve` api.

    This class has some conveninence methods for creating a resource as well
    registering event hooks with the :class:`eve.Eve` api.

    :param name:  The resource name to be registered with the api.
    :param keys:  Strings used as a key for the fields of the resource schema.

    Example::

        persons = Resource('persons', 'first_name', 'last_name')

    """

    def __init__(self, name, *keys):
        self.name = name
        self._key = None  # type: NamedTuple
        self._definition = None  # type: Dict[str, Any]
        self._schema = None  # type: Dict[str, Any]
        self._hooks = None  # type: hooks.Hooks

        if len(keys) > 0:
            self.keys(*keys)

    @property
    def key(self) -> NamedTuple:
        """An optional namedtuple of the fields for the schema fields of an
        instance.

        This get's created if there are args passed in on instantiation or
        by calling the :meth:`keys` method.  If using the :meth:`schema`
        decorator, then this will get passed into the wrapped function, to
        be used in building the schema.

        """
        return self._key

    @property
    def hooks(self):
        """Holds event hooks for that can be registered with an :class:`eve.Eve`
        api.

        .. seealso:: :class:`hooks.Hooks`

        """
        if self._hooks is None:
            self._hooks = hooks.Hooks(self.name)
        return self._hooks

    def keys(self, *keys) -> None:
        """Creates a namedtuple of the keys.

        :param keys:  Strings that are the fields and values for the namedtuple

        """
        Key = namedtuple('Key', keys)
        self._key = Key(*keys)

    def _validate_func(self, func: OptionalFunc, callback: OptionalFunc=None
                       ) -> Any:

        func = utils.callable_or_error(func)

        return callback(func) if callback is not None else func

    @property
    def definition_value(self) -> Dict[str, Any]:
        """The main configuration for an :class:`eve.Eve` domain resource.

        If a value for ``schema`` is set inside the definition_value, then this
        instances :attr:`schema_value` will be ignored. If not then when
        accessing the :meth:`domain` we will use :attr:`schema_value` as the
        value for ``schema`` in the definition.


        .. seealso::
            `Eve Domain Configuration
            <http://python-eve.org/config.html#domain-configuration>`_

        """
        return self._definition if self._definition is not None else {}

    @definition_value.setter
    def definition_value(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise TypeError(data)

        self._definition = data

    @definition_value.deleter
    def definition_value(self):
        del(self._definition)

    @property
    def schema_value(self) -> Dict[str, Any]:
        """The settings for the database and validation portion of the domain
        resource definition.

        This is a :class:`dict` with string keys.  This will get added to the
        definiton when accessing the :meth:`domain` method as the value for
        ``schema`` in the domain resource definition, unless a schema is
        declared in :attr:`definition_value`

        .. seealso::
            `Eve Schema Definition
            <http://python-eve.org/config.html#schema-definition>`_

        """
        return self._schema if self._schema is not None else {}

    @schema_value.setter
    def schema_value(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise TypeError
        self._schema = data

    @schema_value.deleter
    def schema_value(self):
        del(self._schema)

    def definition(self, func: Callable[[], Dict[str, Any]]
                   ) -> Callable[[], Dict[str, Any]]:
        """A decorator that uses the return value of the wrapped function
        to set :attr:`definition_value` for an instance.

        The function should take no args, or kwargs and should return a
        :class:`dict`.  See also: :attr:`definition_value`.

        :raises TypeError: If the return type is not valid for
                           :attr:`definition_value`


        """

        def callback(func):
            self.definition_value = func()

        self._validate_func(func, callback)
        return func

    def schema(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """A decorator that uses the return value of the wrapped function
        to set :attr:`schema_value` for an instance.

        The function can take one arg which will be this instances :attr:`key`
        attribute, will work if the function accepts no args and no kwarrgs as
        well, and should return a :class:`dict`.See also: :attr:`schema_value`.

        :raises TypeError: If the return type is not valid for
                           :attr:`definition_value`

        """
        def callback(func):
            try:
                self.schema_value = func(self.key)
            except TypeError:
                self.schema_value = func()

        self._validate_func(func, callback)
        return func

    def domain(self) -> Dict[str, Any]:
        """Build's the domain resource definition for an instance.

        Uses the :attr:`definition_value` and :attr:`schema_value` to build
        a :class:`dict` that can be used to register an :class:`eve.Eve` api.

        """
        domain = self.definition_value.copy()
        domain.setdefault('schema', self.schema_value)
        return domain

    def init_api(self, api: Eve) -> None:
        """Register's the event hooks with the api and also will register
        the domain with the api, if one does not exist for the resource.

        :param api:  An :class:`eve.Eve` instance.

        :raises TypeError:  If api is not an :class:`eve.Eve` instance.

        """
        if not isinstance(api, Eve):
            raise TypeError(api)
        if self._hooks is not None:
            # add event hooks to the api
            self.hooks.init_api(api)

        # register the domain with the api.
        api.config['DOMAIN'].setdefault(self.name, self.domain())
