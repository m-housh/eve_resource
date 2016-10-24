# -*- coding: utf-8 -*-

from typing import Any, Optional, Iterable

from eve import Eve

from .event import Event, request_event, mongo_event, EventFuncType

# from .exceptions import NotCallable
# from .utils import callable_or_error # , mongo_aliases, request_aliases


class EventHooks(object):
    """An :class:`Event` container that holds events for a domain resource.

    :param resource:  The domain resource
    :param EventType:  The :class:`Event` class or function for the events of
                    this class.

    """
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

        def inner(func: EventFuncType) -> EventFuncType:
            self._make_and_append(event, func)
            return func

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
        def inner(func: EventFuncType) -> EventFuncType:
            for event in events:
                self.event(event, func)
            return func

        return inner(func) if func is not None else inner

    def init_api(self, api: Eve) -> None:
        """Register all event's with an :class:`eve.Eve` instance.

        :param api:  An :class:`eve.Eve` instance

        :raises TypeError:  If api is not an :class:`eve.Eve` instance

        """
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
        self._mongo = None
        self._request = None

    @property
    def mongo(self) -> EventHooks:
        """A :class:`EventHooks` setup for mongo type events that can
        be registered with an :class:`eve.Eve` api.

        """
        if self._mongo is None:
            self._mongo = mongo_hooks(self.resource)
        return self._mongo

    @property
    def request(self) -> EventHooks:
        """A :class:`EventHooks` setup for request type events that can
        be registered with an :class:`eve.Eve` api.

        """
        if self._request is None:
            self._request = request_hooks(self.resource)
        return self._request

    def init_api(self, api: Eve) -> None:
        """Register's the hooks with an :class:`eve.Eve` instance.

        :param api:  A :class:`eve.Eve`

        :raises TypeError:  If ``api`` is not an :class:`eve.Eve` instance

        """

        if not isinstance(api, Eve):
            raise TypeError(api)

        self.mongo.init_api(api)
        self.request.init_api(api)
