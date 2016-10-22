#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from eve_resource.exceptions import NotCallable
from eve_resource import utils


def test_callable_or_error():

    with pytest.raises(NotCallable):
        utils.callable_or_error([])

    def test_func():
        pass

    assert utils.callable_or_error(test_func) == test_func
