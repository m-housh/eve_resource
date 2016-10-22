#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from eve import Eve

from eve_resource import hooks


@pytest.fixture()
def test_func():

    def inner(*args, **kwargs):
        return 'args: {}, kwargs: {}'.format(args, kwargs)

    return inner


def test_Event_parse_event():
    base = hooks.Event('some_event', 'some_resource')
    assert base.event == 'some_event'
    assert base.resource == 'some_resource'
    assert base.func is None


class BaseEventTest(object):

    aliases = None

    def event(self, *args, **kwargs):
        kwargs.setdefault('aliases', self.aliases)
        return hooks.Event(*args, **kwargs)

    def test_aliases(self):

        for key in self.aliases:
            event = self.event(key, 'resource')
            assert event.event == self.aliases[key]

        for value in self.aliases.values():
            event = self.event(value, 'resource')
            assert event.event == value

        with pytest.raises(ValueError):
            self.event('invalid', 'resource')

    def test_set_func(self):

        event_key = list(self.aliases.values())[0]
        event = self.event(event_key, 'some_resource')

        @event.set_func
        def test(items):
            return 'test_func'

        assert event.func(None) == 'test_func'

    def test_register(self, test_func):
        event_key = list(self.aliases.values())[1]
        event = self.event(event_key, 'some_resource', test_func)
        app = Eve(settings={'DOMAIN': {}})

        event.register(app)
        assert len(getattr(app, event_key)) == 1

        with pytest.raises(TypeError):
            event.register(None)

    def test_call(self, test_func):
        event_key = list(self.aliases.values())[-1]
        event = self.event(event_key, 'some_resource', test_func)
        assert event('some_resource', 'arg1', value='something') == \
            "args: ('arg1',), kwargs: {'value': 'something'}"

        # func not set return's None, if this is registered with a live
        # api, don't break things.
        event2 = self.event(event_key, 'resource')
        assert event2('resource', 'arg1', value='something') is None


class TestMongoEvent(BaseEventTest):

    @classmethod
    def setup_class(cls):
        cls.aliases = hooks._mongo_aliases()

    def test_repr(self):
        msg = "Event('on_inserted', 'resource', func=None,"
        msg += ' aliases={})'.format(self.aliases)

        assert repr(self.event('inserted', 'resource')) == msg

    def test_mongo_event(self):
        event = hooks.mongo_event('updated', 'resource')
        assert isinstance(event, hooks.Event)
        assert event.aliases == self.aliases


class TestRequestEvent(BaseEventTest):

    @classmethod
    def setup_class(cls):
        cls.aliases = hooks._request_aliases()

    def test_repr(self):
        msg = "Event('on_pre_GET', 'resource', func=None,"
        msg += ' aliases={})'.format(self.aliases)
        rep = repr(self.event('pre_GET', 'resource'))
        print(rep)
        assert rep == msg

    def test_request_event(self):
        event = hooks.request_event('post_PATCH', 'resource')
        assert isinstance(event, hooks.Event)
        assert event.aliases == self.aliases


class TestBaseHooks(object):

    HookClass = hooks.EventHooks

    @classmethod
    def setup_class(cls):
        pass

    def test_event(self, test_func):
        instance = self.HookClass('resource')

        assert len(instance.events) == 0

        @instance.event('some_event')
        def some_func(items):
            pass

        assert len(instance.events) == 1

        instance.event('another_event', test_func)
        assert len(instance.events) == 2

        with pytest.raises(TypeError):
            instance.event({}, test_func)

        event = hooks.Event('event', 'resource')
        instance.event(event)
        assert len(instance.events) == 3

        invalid_event = hooks.Event('event', 'not_resource')
        with pytest.raises(ValueError):
            instance.event(invalid_event)

    def test_multi_event(self, test_func):
        instance = self.HookClass('resource')

        @instance.multi_event('a', 'b', 'c')
        def test(*args, **kwargs):
            pass

        assert len(instance.events) == 3

        instance.multi_event('d', 'e', func=test_func)
        assert len(instance.events) == 5


def test_mongo_hooks():
    mongo = hooks.mongo_hooks('resource')

    @mongo.multi_event('insert', 'inserted')
    def test_func(*args, **kwargs):
        pass

    assert len(mongo.events) == 2

    app = Eve(settings={'DOMAIN': {}})

    assert len(app.on_insert) == 0
    assert len(app.on_inserted) == 0

    mongo.init_api(app)

    assert len(app.on_insert) == 1
    assert len(app.on_inserted) == 1

    with pytest.raises(TypeError):
        mongo.init_api(None)


def test_request_hooks(test_func):
    requests = hooks.request_hooks('resource')
    requests.event('pre_DELETE', test_func)

    assert len(requests.events) == 1

    rep = repr(requests)
    assert 'resource' in rep


def test_Hooks(test_func):
    _hooks = hooks.Hooks('resource')
    assert isinstance(_hooks.mongo, hooks.EventHooks)
    assert len(_hooks.mongo.events) == 0
    assert isinstance(_hooks.requests, hooks.EventHooks)
    assert len(_hooks.requests.events) == 0

    _hooks.mongo.event('insert', test_func)
    _hooks.requests.event('post_PATCH', test_func)

    api = Eve(settings={'DOMAIN': {}})
    assert len(api.on_insert) == 0
    assert len(api.on_post_PATCH) == 0

    _hooks.init_api(api)
    assert len(api.on_insert) == 1
    assert len(api.on_post_PATCH) == 1

    with pytest.raises(TypeError):
        _hooks.init_api({})
