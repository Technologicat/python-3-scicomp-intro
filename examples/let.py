#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Some "Lisp let"-ish constructs in Python.

TODO: let*, letrec. Currently this supports only the basic "parallel binding" let.

Inspiration:
    https://nvbn.github.io/2014/09/25/let-statement-in-python/
    https://stackoverflow.com/questions/12219465/is-there-a-python-equivalent-of-the-haskell-let
    http://sigusr2.net/more-about-let-in-python.html

Created on Mon Apr 30 13:51:47 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

class env:
    """Context manager aware bunch. Also works as a bare bunch.

    Usage:
        # with context manager:
        with env(x = 0) as myenv:
            print(myenv.x)
        # DANGER: myenv still exists due to Python's scoping rules.

        # bare bunch:
        myenv2 = env(s="hello", orange="fruit", answer=42)
        print(myenv2.s)
        print(myenv2)
"""
    def __init__(self, **bindings):
        self._env = {}
        for name,value in bindings.items():
            self._env[name] = value

    def __setattr__(self, name, value):
        if name == "_env":  # hook to allow creating _env directly in self
            return super().__setattr__(name, value)
        self._env[name] = value  # make all other attrs else live inside _env

    def __getattr__(self, name):
        env = self._env   # __getattr__ not called if direct attr lookup succeeds, no need for hook.
        if name in env:
            return env[name]
        else:
            raise AttributeError("Name '{:s}' not in environment".format(name))

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        # we could nuke the *contents*, but it's simpler and more predictable not to.
        pass

    def __str__(self):  # just for pretty-printing
        bindings = ["{}: {}".format(name,value) for name,value in self._env.items()]
        return "<env: <{:s}>>".format(", ".join(bindings))

def letexpr(body, **bindings):
    """let expression, for use with lambdas.

    Example: a list uniqifier:

        f = lambda lst: letexpr(seen=set(),
                                body=lambda env: [env.seen.add(x) or x for x in lst if x not in env.seen])

    Parameters:
        `body`: one-argument function to run, taking an `env` instance that contains the "let" bindings.
                (Take advantage of free variables and lexical scoping to pass in other stuff if needed.)

        Everything else: "let" bindings; each argument name is bound to its value.

    Returns:
        The value returned by body.
"""
    return body(env(**bindings))

# decorator factory: almost as fun as macros?
def let_over_def(**bindings):            # decorator factory
    """let decorator, for use with named functions.

    Named after "let over lambda", since this version of "let" can only
    sit above a "def".

    Usage is similar to the Lisp idiom: this gives a local environment
    that can be used to stash data to be preserved between calls.

    Usage:

    @let_over_def(y = 23, z = 42)
    def foo(x, env=None):  # env is filled in by the decorator
        print(x, env.y, env.z)
    foo(17)

    @let_over_def(count = 0)
    def counter(env=None):
        env.count += 1
        return env.count
    print(counter())
    print(counter())
    print(counter())

    The named argument `env` is an env instance that contains the let bindings;
    all other args and kwargs are passed through.
"""
    def deco(body):                      # decorator
        # evaluate env when the function def runs!
        # (so that any mutations to its state are preserved
        #  between calls to the decorated function)
        env_instance = env(**bindings)
        def decorated(*args, **kwargs):  # decorated function (replaces original body)
            kwargs_with_env = kwargs.copy()
            kwargs_with_env["env"] = env_instance
            return body(*args, **kwargs_with_env)
        return decorated
    return deco

def immediate(thunk):
    """Decorator: run immediately, overwrite function by its return value.

    Can be used to make lispy not-quite-functions where the def just delimits
    a block of code that runs immediately (like call-with-something in Lisp).
    Convenient e.g. for escaping nested loops (by using return).

    The function must be callable with zero arguments.

    Usage:

    @immediate
    def result():  # this block of code runs immediately
        return "hello"
    print(result)  # "hello"

    # can use a dummy name if the return value is of no interest:
    @immediate
    def _():
        ... # code with cheeky side effects goes here
"""
    return thunk()

def let(**bindings):
    """let block, for use with a def.

    This is a decorator chain, first applying @let_over_def, then @immediate.

    In effect, this makes the def the body of the let, and runs it immediately.

    Usage:

    @let(x=17, y=23)
    def result(env=None):
        print(env.x, env.y)
        return env.x + env.y
    print(result)  # 40

    # can use a dummy name if the return value is of no interest:
    @let(s="hello")
    def _(env=None):
        print(env.s)
"""
    let_over_def_deco = let_over_def(**bindings)
    def deco(body):
        return immediate(let_over_def_deco(body))
    return deco


############################################################
# Examples / tests
############################################################

# "let over lambda"-ish
#   - DANGER: "myenv" is bound in the surrounding scope; not what we want.
#   - If we have several of these in the same scope, the latest "myenv"
#     will win, overwriting the others. So a better solution is needed.
#
with env(x = 0) as myenv:
    def g():
        myenv.x += 1
        return myenv.x

# Abusing mutable default args gives true "let over lambda" behavior:
#
def h(_myenv = {"x": 0}):
    _myenv["x"] += 1
    return _myenv["x"]

# Combining these strategies (bunch, without context manager):
#
def i(_myenv = env(x = 0)):
    _myenv.x += 1
    return _myenv.x

# The decorator factory also gives us true "let over lambda" behavior:
#
@let_over_def(x = 0)
def j(env):
    env.x += 1
    return env.x


def uniqify_test():
    # the named function solution:
    def f(lst):
        seen = set()
        def see(x):
            seen.add(x)
            return x
        return [see(x) for x in lst if x not in seen]

    # the one-liner:
    f2 = lambda lst: (lambda seen: [seen.add(x) or x for x in lst if x not in seen])(seen=set())

    # we essentially want something like this:
    def f3(lst):
        with env(seen = set()) as myenv:
            return [myenv.seen.add(x) or x for x in lst if x not in myenv.seen]

    # using the above letexpr:
    f4 = lambda lst: letexpr(seen=set(),
                             body=lambda env: [env.seen.add(x) or x for x in lst if x not in env.seen])

    # testing:
    #
    L = [1, 1, 3, 1, 3, 2, 3, 2, 2, 2, 4, 4, 1, 2, 3]

    # Call each implementation twice to demonstrate that a fresh `seen`
    # is indeed created at each call.
    #
    print(f(L))
    print(f(L))

    print(f2(L))
    print(f2(L))

    print(f3(L))
    print(f3(L))

    print(f4(L))
    print(f4(L))

if __name__ == '__main__':
    uniqify_test()

    print(g())
    print(g())
    print(g())
    print(myenv)  # DANGER: visible from here

    print(h())
    print(h())
    print(h())

    print(i())
    print(i())
    print(i())

    print(j())
    print(j())
    print(j())

    ################################

    @let_over_def(y = 23)
    def foo(x, env):  # the named argument env contains the let bindings
        print(x, env.y)
    foo(17)

    ################################

    # Lexical scoping - actually, just by borrowing Python's:
    #
    @let_over_def(x = 5)
    def bar(env):
        print("in bar x is", env.x)

        @let_over_def(x = 42)
        def baz(env):  # this env shadows the outer env
            print("in baz x is", env.x)
        baz()

        print("in bar x is still", env.x)
    bar()

    ################################

    # To eliminate the explicit calls, @immediate from lecture 11, slide 33:
    #
    @immediate
    @let_over_def(x = 5)
    def _(env):  # this is now the let block
        print("outer x is", env.x)

        @immediate
        @let_over_def(x = 42)
        def _(env):
            print("inner x is", env.x)

        print("outer x is still", env.x)

    ################################

    # With a combined decorator:
    #
    @let(x = 5)
    def _(env):  # the body of the let block
        print("outer x is", env.x)

        @let(x = 42)
        def _(env):
            print("inner x is", env.x)

        print("outer x is still", env.x)

    ################################

    # reinterpreting the idea of "immediate" is also a possible approach:
    letify = lambda thunk: thunk()

    @letify
    def _(x = 1):
        # ...this is just a block of code with the above bindings...
        return x*42  # ...but we can also return to break out of it early, if needed.
    print(_)  # the def'd "function" is replaced by its return value
