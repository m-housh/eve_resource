# -*- coding: utf-8 -*-

from typing import Optional, Any, Callable, Dict

from eve import Eve

from .utils import callable_or_error, mongo_aliases, request_aliases

from .exceptions import NotCallable

AliasType = Dict[str, str]
EventFuncType = Callable[..., Any]


class Event(object):
    """Holds a function to register with an :class:`eve.Eve` instance as an
    event hook.

    This class acts as the function, when the :class:`eve.Eve` event hook is
    fired, we check that the resource matches the :attr:`resource` for this
    instance and if it does we call the :attr:`func` for this instance.

    :param event:  A string of the :class:`eve.Eve` event to register the
                function for.  This can also be a valid value in
                :attr:`aliases`
    :param resource:  The :class:`eve.Eve` domain resource the function is for.
    :param func:  A callable that's called as the event hook.
    :param aliases:  A :class:`dict` with keys being strings of valid
                convenience aliases a user can use to register an event, the
                value for the key should be the valid :class:`eve.Eve` event.

    .. seealso: `Eve Event Hooks
                <http://python-eve.org/features.html#event-hooks>`_

    """
    def __init__(self, event: str, resource: str,
                 func: Optional[EventFuncType]=None,
                 aliases: Optional[AliasType]=None) -> None:

        self.aliases = aliases
        self.event = self.parse_event(event)
        self.resource = resource
        self.func = callable_or_error(func) if func is not None else None

    def parse_event(self, event: str) -> str:
        """Parses an event, returning a valid event that can be registered
        with an ``Eve`` instance.

        :param event: A string to check if it's valid.  If no aliases are set
                      for a class, then this will just return the input event.

        :raises ValueError:  If :attr:`aliases` is not ``None`` and the event
                             is not a valid alias.

        """
        if self.aliases is not None:
            if event in self.aliases.keys():
                return self.aliases[event]
            elif event in self.aliases.values():
                return event
            else:
                # make this a better error
                raise ValueError(event)
        return event

    def set_func(self, func: EventFuncType) -> EventFuncType:
        """Set's the func for an instance, can be used as a decorator.

        :param func:  The func to set on the instance.

        :raises NotCallable:  If the func is not callable.

        """
        self.func = callable_or_error(func)
        return func

    def register(self, app: Eve) -> None:
        """Register's an instance with an :class:`eve.Eve` instance.

        :param app:  The :class:`eve.Eve` instance to register the event with.

        """
        if not isinstance(app, Eve):
            raise TypeError(app)

        attr = getattr(app, self.event, None)

        if attr is not None:
            attr += self
        # else raise Error

    def __call__(self, resource, *args, **kwargs) -> Any:
        """Call the :attr:`func` if the resource matches.

        """
        if resource == self.resource:
            try:
                return callable_or_error(self.func)(*args, **kwargs)
            except NotCallable:
                pass

    def __repr__(self) -> str:
        return (
            "{n}('{e}', '{r}', func={f}, aliases={a})".format(
                n=self.__class__.__name__,
                e=self.event,
                r=self.resource,
                f=self.func,
                a=self.aliases
            )
        )


def mongo_event(event: str, resource: str, func: Optional[EventFuncType]=None
                ) -> Event:
    """A function to return an :class:`Event` with aliases set-up for mongo
    events.

    The following aliases can be used for mongo events::

        +----------+--------------+
        | Alias    |   Eve Event  |
        +==========+==============+
        | insert   | on_insert    |
        +----------+--------------+
        | inserted | on_inserted  |
        +----------+--------------+
        | fetch    | on_fetch     |
        +----------+--------------+
        | fetched  | on_fetched   |
        +----------+--------------+
        | replace  | on_replace   |
        +----------+--------------+
        | replaced | on_replaced  |
        +----------+--------------+
        | update   | on_update    |
        +----------+--------------+
        | updated  | on_updated   |
        +----------+--------------+
        | delete   | on_deleted   |
        +----------+--------------+

    """
    return Event(event, resource, func, mongo_aliases())


def request_event(event: str, resource: str, func: Optional[EventFuncType]=None
                  ) -> Event:
    """A function to return an :class:`Event` with aliases set-up for request
    events.

    The following aliases can be used for request events::

        +--------------+-----------------+
        | Alias        |   Eve Event     |
        +==============+=================+
        |  pre_GET     | on_pre_GET      |
        +--------------+-----------------+
        | post_GET     | on_post_GET     |
        +--------------+-----------------+
        | pre_PUT      | on_pre_PUT      |
        +--------------+-----------------+
        | post_PUT     | on_post_PUT     |
        +--------------+-----------------+
        | pre_PATCH    | on_pre_PATCH    |
        +--------------+-----------------+
        | post_PATCH   | on_post_PATCH   |
        +--------------+-----------------+
        | pre_POST     | on_pre_POST     |
        +--------------+-----------------+
        | post_POST    | on_post_POST    |
        +--------------+-----------------+
        | pre_DELETE   | on_pre_DELETE   |
        +--------------+-----------------+
        | post_DELETE  | on_post_DELETE  |
        +--------------+-----------------+

    """
    return Event(event, resource, func, request_aliases())
