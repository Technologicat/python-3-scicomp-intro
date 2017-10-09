#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dynamic scope emulation by Jason Orendorff, 2010.

This module exports a single object instance, env, which emulates dynamic scoping
(Lisp's special variables).

- Dynamic variables are created by 'with env.let()'.
- The created dynamic variables exist while the with block is executing,
  and fall out of scope when the with block exits.
- The blocks can be nested. Inner scopes mask outer ones, as usual.

Example:

    from dynscope import env

    with env.let(a=2, b="foo"):
        print(env.a)  # prints 2
        f()           # call a function that uses env.a or env.b

        with env.let(a=3):
            print(env.a)  # 3

        print(env.a)  # 2

    print(env.b)      # AttributeError, env.b no longer exists

Source:

    https://stackoverflow.com/questions/2001138/how-to-create-dynamical-scoped-variables-in-python
"""

from threading import local

_L = local()  # each thread gets its own stack
_L._stack = []

class _EnvBlock(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
    def __enter__(self):
        _L._stack.append(self.kwargs)
    def __exit__(self, t, v, tb):
        _L._stack.pop()

class _Env(object):
    def __getattr__(self, name):
        for scope in reversed(_L._stack):
            if name in scope:
                return scope[name]
        raise AttributeError("no variable '%s' in environment" % (name))
    def let(self, **kwargs):
        return _EnvBlock(kwargs)
    def __setattr__(self, name, value):
        raise AttributeError("env variables can only be set using 'with env.let()'")

env = _Env()