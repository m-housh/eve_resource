#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_eve_resource
----------------------------------

Tests for `eve_resource` module.
"""

import pytest
from eve import Eve

from eve_resource import resource


@pytest.fixture()
def accounts():
    return resource.Resource('accounts', 'username', 'password')


@pytest.fixture()
def definition():
    return {
        'item_title': 'account',
        'public_methods': ['GET'],
    }


@pytest.fixture()
def schema(accounts):
    return {
        accounts.key.username: {
            'type': 'string',
            'required': True,
        },
        accounts.key.password: {
            'type': 'string',
            'required': True,
        },
    }


class TestEve_resource(object):

    @classmethod
    def setup_class(cls):
        pass

    def test_key(self, accounts):
        # accounts = resource.Resource('accounts', 'username', 'password')
        assert accounts.name == 'accounts'
        assert accounts.key.username == 'username'
        assert accounts.key.password == 'password'
        assert len(accounts.key) == 2

    def test_definition(self, accounts, definition):
        assert accounts.definition_value == {}

        @accounts.definition
        def wrapped_def():
            return definition

        assert accounts.definition_value == definition
        del(accounts.definition_value)
        with pytest.raises(TypeError):
            accounts.definition_value = 'not a dict'

    def test_schema(self, accounts, schema):
        assert accounts.schema_value == {}

        @accounts.schema
        def wrapped_schema():
            """Wrapped schema doc"""
            return schema

        assert accounts.schema_value == schema
        assert wrapped_schema.__doc__ == """Wrapped schema doc"""

        del(accounts.schema_value)

        with pytest.raises(TypeError):
            accounts.schema_value = 'not a dict'

        @accounts.schema
        def schema2(key):
            return {
                key.username: {
                    'type': 'string',
                    'required': True,
                },
                key.password: {
                    'type': 'string',
                    'required': True,
                },
            }

        assert accounts.schema_value == schema

    def test_domain(self, accounts, definition, schema):

        accounts.schema_value = schema
        assert accounts.domain() == {'schema': schema}

        accounts.definition_value = definition

        value = definition.copy()
        value['schema'] = schema

        assert accounts.domain() == value

    def test_init_api(self, accounts):
        app = Eve(settings={'DOMAIN': {}})
        assert len(app.on_insert) == 0

        @accounts.hooks.mongo('insert')
        def test(items):
            pass

        accounts.init_api(app)
        assert len(app.on_insert) == 1

        @accounts.hooks.request('pre_GET', 'post_POST')
        def tes2(*args, **kwargs):
            pass

        assert len(app.on_pre_GET) == 0
        assert len(app.on_post_POST) == 0

        accounts.init_api(app)
        assert len(app.on_pre_GET) == 1
        assert len(app.on_post_POST) == 1

        assert app.config['DOMAIN'].get('accounts') is not None

        with pytest.raises(TypeError):
            accounts.init_api(None)

    @classmethod
    def teardown_class(cls):
        pass
