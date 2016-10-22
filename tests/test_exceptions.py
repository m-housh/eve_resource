#!/usr/bin/env python
# -*- coding: utf-8 -*-


from eve_resource.exceptions import EveResourceError, NotCallable


def test_NotCallable():
    exc = NotCallable({})
    assert isinstance(exc, EveResourceError)
    assert isinstance(exc, TypeError)
    assert str(exc) == "<class 'dict'> is not callable"
