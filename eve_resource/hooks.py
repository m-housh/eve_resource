# -*- coding: utf-8 -*-

from typing import Dict, Any, Callable, Optional, Iterable

from eve import Eve

from .exceptions import NotCallable
from .utils import callable_or_error

AliasType = Dict[str, str]
EventFuncType = Callable[..., Any]


def _mongo_aliases() -> AliasType:
    """Creates aliases for mongo events."""
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


def _request_aliases() -> AliasType:
    """Creates aliases for request events"""
    keys = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')

    rv = {}  # type: AliasType
    for key in keys:
        rv['pre_' + key] = 'on_pre_' + key
        rv['post_' + key] = 'on_post_' + key

    return rv


class Event(object):
    """Holds a function to register with an :class:`eve.Eve` instance as an
    event hook.

    :param event:  The :class:`eve.Eve` event to register the function for.
    :param resource:  The :class:`eve.Eve` domain resource the function is for.
    :param func:  A callable that's called as the event hook.

    """

    # aliases = None  # type: AliasType

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

    def set_func(self, func: EventFuncType) -> None:
        """Set's the func for an instance, can be used as a decorator.

        :param func:  The func to set on the instance.

        """
        self.func = callable_or_error(func)

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

    """
    return Event(event, resource, func, _mongo_aliases())


def request_event(event: str, resource: str, func: Optional[EventFuncType]=None
                  ) -> Event:
    """A function to return an :class:`Event` with aliases set-up for request
    events.

    """
    return Event(event, resource, func, _request_aliases())


class EventHooks(object):

    def __init__(self, resource: str, EventType=Event) -> None:
        self.EventType = EventType
        self.resource = resource
        self.events = []

    def _make_and_append(self, event: str, func: EventFuncType) -> None:
        """Creates a new event and appends to events."""
        self.events.append(
            self.EventType(event, self.resource, func)
        )

    def event(self, event: Any, func: Optional[EventFuncType]=None
              ) -> Optional[EventFuncType]:
        """Add's an event to the instance.

        :param event:  A string or instance of :attr:`EventType`.
        :param func:  A callable to register, only used if ``event`` is a
                      string, that we use to create an instance of
                      :attr:`EventType`

        """

        def inner(func: EventFuncType) -> None:
            return self._make_and_append(event, func)

        if isinstance(event, str):
            return inner if func is None else inner(func)

        if isinstance(event, self.EventType):
            if event.resource != self.resource:
                raise ValueError('event resource does not match.')
            return self.events.append(event)

        raise TypeError('{} should be string or {}'.format(
            event, self.EventType.__name__)
        )

    def multi_event(self, *events, func: Optional[EventFuncType]=None
                    ) -> Optional[EventFuncType]:
        """Register's the same function for multiple events. Can be used as
        a decorator.

        :param events:  Iterable of strings that are the api events to register
                        the function with.
        :param func:  The function to use for the api hook event.

        """
        def inner(func: EventFuncType) -> None:
            for event in events:
                self.event(event, func)

        return inner(func) if func is not None else inner

    def init_api(self, api: Eve) -> None:
        if not isinstance(api, Eve):
            raise TypeError(api)

        for event in self:
            event.register(api)

    def __iter__(self) -> Iterable[Any]:
        return iter(self.events)

    def __repr__(self) -> str:
        return "{n}('{r}', EventType={e})".format(
            n=self.__class__.__name__,
            r=self.resource,
            e=self.EventType
        )

    def __call__(self, *events, func: Optional[EventFuncType]=None) -> Any:
        """Calls the appropriate :meth:`event` or :meth:`multi_event` with
        the given parameters.  Can be used as a decorator.

        :param events:  A single event string or multiple event strings.
                        If the lenght is 1, then we call :meth:`event` else
                        we call :meth:`multi_event`.
        :param func:  The function to add as the event.

        """
        def inner(func: EventFuncType):
            if len(events) == 1:
                return self.event(events[0], func=func)
            return self.multi_event(*events, func=func)

        return inner(func) if func is not None else inner


def mongo_hooks(resource: str) -> EventHooks:
    """Returns a :class:`EventHooks` set-up for mongo events.

    """
    return EventHooks(resource, mongo_event)


def request_hooks(resource: str) -> EventHooks:
    """Returns a :class:`EventHooks` set-up for request events.

    """
    return EventHooks(resource, request_event)


class Hooks(object):
    """Container object that holds :class:`EventHooks` for mongo and
    request events.

    :param resource:  The domain resource the hooks are for.

    """

    def __init__(self, resource: str) -> None:
        self.resource = resource
        self.mongo = mongo_hooks(self.resource)
        self.requests = request_hooks(self.resource)

    def init_api(self, api: Eve) -> None:
        """Register's the hooks with an :class:`eve.Eve` instance.

        :param api:  A :class:`eve.Eve`

        :raises TypeError:  If ``api`` is not an :class:`eve.Eve` instance

        """

        if not isinstance(api, Eve):
            raise TypeError(api)

        self.mongo.init_api(api)
        self.requests.init_api(api)
