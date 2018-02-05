#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Environment that disallows rebinding names, for use with the context manager.

Really simplistic, essentially has just a single scope; but demonstrates
the use of __setattr__ and __getattr__.

Created on Mon Feb  5 21:57:56 2018

@author: jje
"""

# To be able to create __env__, in __setattr__ we must special-case it,
# falling back to default behaviour (which is object.__setattr__,
# hence super().__setattr__).
#
# __getattr__ is never called if standard attribute lookup succeeds,
# so there we don't need a hook for __env__ (as long as we don't try to
# look up __env__ before it is created).
#
# __enter__ should "return self" to support the binding form "with ... as ...".
#
# https://docs.python.org/3/reference/datamodel.html#object.__setattr__
# https://docs.python.org/3/reference/datamodel.html#object.__getattr__

class no_rebind:
    def __init__(self):
        self.__env__ = {}

    def __setattr__(self, name, value):
        if name == "__env__":
            return super().__setattr__(name, value)

        env = self.__env__
        if name not in env:
            env[name] = value
        else:
            raise AttributeError("Attempted to rebind name '{:s}'".format(name))

    def __getattr__(self, name):
        env = self.__env__
        if name in env:
            return env[name]
        else:
            raise AttributeError("Name '{:s}' not in environment".format(name))

    def __enter__(self):
        return self

    def __exit__(self, exctype, excvalue, traceback):
        pass

# Usage example / unit test:
#
def test():
    with no_rebind() as e:  # now e is an environment that disallows rebind
        try:
            e.a = 2  # should succeed, empty environment so far
            e.b = 3  # should succeed, different name
            print(e.a, e.b)
        except AttributeError:
            print('Test 1 FAILED')
        else:
            print('Test 1 PASSED')

        try:
            e.a = 5  # should fail, e.a is already bound
            print(e.a)
        except AttributeError:
            print('Test 2 PASSED')
        else:
            print('Test 2 FAILED')

if __name__ == '__main__':
    test()
