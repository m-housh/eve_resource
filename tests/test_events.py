#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from eve import Eve

from eve_resource import event
from eve_resource import utils


@pytest.fixture()
def test_func():

    def inner(*args, **kwargs):
        return 'args: {}, kwargs: {}'.format(args, kwargs)

    return inner


def test_Event_parse_event():
    base = event.Event('some_event', 'some_resource')
    assert base.event == 'some_event'
    assert base.resource == 'some_resource'
    assert base.func is None


class BaseEventTest(object):

    aliases = None

    def event(self, *args, **kwargs):
        kwargs.setdefault('aliases', self.aliases)
        return event.Event(*args, **kwargs)

    def test_aliases(self):

        for key in self.aliases:
            _event = self.event(key, 'resource')
            assert _event.event == self.aliases[key]

        for value in self.aliases.values():
            _event = self.event(value, 'resource')
            assert _event.event == value

        with pytest.raises(ValueError):
            self.event('invalid', 'resource')

    def test_set_func(self):

        event_key = list(self.aliases.values())[0]
        _event = self.event(event_key, 'some_resource')

        @_event.set_func
        def test(items):
            return 'test_func'

        assert _event.func(None) == 'test_func'

    def test_register(self, test_func):
        event_key = list(self.aliases.values())[1]
        _event = self.event(event_key, 'some_resource', test_func)
        app = Eve(settings={'DOMAIN': {}})

        _event.register(app)
        assert len(getattr(app, event_key)) == 1

        with pytest.raises(TypeError):
            _event.register(None)

    def test_call(self, test_func):
        event_key = list(self.aliases.values())[-1]
        _event = self.event(event_key, 'some_resource', test_func)
        assert _event('some_resource', 'arg1', value='something') == \
            "args: ('arg1',), kwargs: {'value': 'something'}"

        # func not set return's None, if this is registered with a live
        # api, don't break things.
        event2 = self.event(event_key, 'resource')
        assert event2('resource', 'arg1', value='something') is None


class TestMongoEvent(BaseEventTest):

    @classmethod
    def setup_class(cls):
        cls.aliases = utils.mongo_aliases()

    def test_repr(self):
        msg = "Event('on_inserted', 'resource', func=None,"
        msg += ' aliases={})'.format(self.aliases)

        assert repr(self.event('inserted', 'resource')) == msg

    def test_mongo_event(self):
        _event = event.mongo_event('updated', 'resource')
        assert isinstance(_event, event.Event)
        assert _event.aliases == self.aliases


class TestRequestEvent(BaseEventTest):

    @classmethod
    def setup_class(cls):
        cls.aliases = utils.request_aliases()

    def test_repr(self):
        msg = "Event('on_pre_GET', 'resource', func=None,"
        msg += ' aliases={})'.format(self.aliases)
        rep = repr(self.event('pre_GET', 'resource'))
        print(rep)
        assert rep == msg

    def test_request_event(self):
        _event = event.request_event('post_PATCH', 'resource')
        assert isinstance(_event, event.Event)
        assert _event.aliases == self.aliases
