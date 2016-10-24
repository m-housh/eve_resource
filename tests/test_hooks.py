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
    assert isinstance(_hooks.request, hooks.EventHooks)
    assert len(_hooks.request.events) == 0

    _hooks.mongo.event('insert', test_func)
    _hooks.request.event('post_PATCH', test_func)

    api = Eve(settings={'DOMAIN': {}})
    assert len(api.on_insert) == 0
    assert len(api.on_post_PATCH) == 0

    _hooks.init_api(api)
    assert len(api.on_insert) == 1
    assert len(api.on_post_PATCH) == 1

    with pytest.raises(TypeError):
        _hooks.init_api({})
