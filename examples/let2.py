#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Introduce local bindings.

The forms "let" and "letrec" are supported(-ish). As a bonus, we provide the
"begin" and "begin0" sequencing forms, like Racket.

This version uses a lispy syntax. Left-to-right eager evaluation of tuples
in Python allows us to provide sequential assignments.

Based on a StackOverflow answer by divs1210:
    https://stackoverflow.com/a/44737147

In the basic parallel binding "let" form, bindings are independent
(do not see each other).

Example:

    let((('a', 1),
         ('b', 2)),
        lambda o: [o.a, o.b])

gives: [1, 2]

In "letrec", bindings down the chain can depend on the ones above them
through a lambda.

Example:

    letrec((('a', 1),
            ('b', lambda o: o.a + 1)),
           lambda o: o.b)

gives: 2

DANGER: in "letrec", **any** callable as a value for a binding is interpreted
as a one-argument function that takes an environment.

If you need to define a function (lambda) in a "letrec", wrap it
in a  lambda o: ...  even if it doesn't need the environment:

    letrec((('a', 1),
            ('b', lambda o: o.a + 1),          # just a value that uses env
            ('f', lambda o: lambda x: 42*x)),  # a function, whether or not uses env
           lambda o: o.b * o.f(1))

gives: 84

In "letrec", mutually recursive functions are also possible. Example:

    letrec((('evenp', lambda o: lambda x: (x == 0) or  o.oddp(x - 1)),
            ('oddp',  lambda o: lambda x: (x != 0) and o.evenp(x - 1))),
           lambda o: o.evenp(42))

Decorator versions of both "let" and "letrec" are provided, for let-over-def:

    @dlet((('x', 17),))
    def foo(*, env):
        return env.x
    foo()

gives: 17

    @dletrec((('x', 2),
              ('y', lambda o: o.x + 3)))
    def bar(a, *, env):
        return a + env.y
    bar(10)

gives: 15

The environment is passed in by name, as "env". The function can take
any other arguments as usual.

Let-over-def provides a local storage that persists across calls:

    @dlet((('count', 0),))
    def counter(*, env):
        env.count += 1
        return env.count
    counter()
    counter()
    print(counter())

gives: 3

A let-over-lambda is also possible:

    lc = let((('count', 0),),
             lambda o: lambda: begin(o.set('count', o.count + 1),
                                     o.count))
    lc()
    lc()
    print(lc())

gives: 3

Here the environment is passed to the  lambda o: ...  as usual.

Created on Wed Jun 27 15:03:48 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

# API

def let(bindings, body):
    """let expression."""
    return _let(bindings, body)

def letrec(bindings, body):
    """letrec expression."""
    return _let(bindings, body, mode="letrec")

def dlet(bindings):
    """let decorator."""
    return _dlet(bindings)

def dletrec(bindings):
    """letrec decorator."""
    return _dlet(bindings, mode="letrec")

def begin(*vals):   # eager, bodys already evaluated when this is called
    """Racket-like begin: return the last value."""
    return vals[-1]

def begin0(*vals):  # eager, bodys already evaluated when this is called
    """Racket-like begin0: return the first value."""
    return vals[0]

# implementation

class _env:
    """Environment; used as storage for local bindings."""

    def set(self, k, v):
        """Convenience method to allow assignment in expression contexts.

        For extra convenience, return the assigned value.

        DANGER: avoid the name k="set"; it will happily shadow this method,
        because instance attributes are seen before class attributes."""
        setattr(self, k, v)
        return v

def _let(bindings, body, env=None, mode="let"):
    assert mode in ("let", "letrec")

    if not len(bindings):
        # decorators just need the final env; else run body now
        return env if body is None else body(env)

    env = env or _env()
    (k, v), *more = bindings

    if mode == "letrec" and callable(v):
        v = v(env)

    setattr(env, k, v)

    return _let(more, body, env, mode)

def _dlet(bindings, mode="let"):  # let and letrec decorator factory
    def deco(body):
        env = _let(bindings, body=None, mode=mode)  # set up env, don't run yet
        def decorated(*args, **kwargs):
            kwargs_with_env = kwargs.copy()
            kwargs_with_env["env"] = env
            return body(*args, **kwargs_with_env)
        return decorated
    return deco


def _test():
    x = let((('a', 1),
             ('b', 2)),
            lambda o: o.a + o.b)
    assert x == 3

    x = letrec((('a', 1),
                ('b', lambda o: o.a + 2)),  # hence, b = 3
               lambda o: o.a + o.b)
    assert x == 4

    t = letrec((('evenp', lambda o: lambda x: (x == 0) or  o.oddp(x - 1)),
                ('oddp',  lambda o: lambda x: (x != 0) and o.evenp(x - 1))),
               lambda o: o.evenp(42))
    assert t == True

    f = lambda x: begin(print("hi there, I'm a side effect in a lambda"),
                        42*x)
    assert f(1) == 42

    g = lambda x: begin0(23*x,
                         print("hi there, I'm also a side effect in a lambda"))
    assert g(1) == 23

    @dlet((('x', 17),))
    def foo(*, env):
        return env.x
    assert foo() == 17

    @dletrec((('x', 2),
              ('y', lambda o: o.x + 3)))
    def bar(a, *, env):
        return a + env.y
    assert bar(10) == 15

    @dlet((('count', 0),))
    def counter(*, env):
        env.count += 1
        return env.count
    counter()
    counter()
    assert counter() == 3

    # let-over-lambda
    lc = let((('count', 0),),
             lambda o: lambda: begin(o.set('count', o.count + 1),
                                     o.count))
    lc()
    lc()
    assert lc() == 3

    print("All tests passed")

if __name__ == '__main__':
    _test()
