#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Some "Lisp let"-ish constructs in Python.

The forms "let" and "letrec" are supported(-ish). As a bonus, we provide the
"begin" and "begin0" sequencing forms, like Racket.

In the basic parallel binding "let" form, bindings are independent
(do not see each other).

The sequential binding form "let*" is **not** supported by this implementation.

In "letrec", any binding can refer to any other. However, this implementation
of letrec is only intended for locally defining mutually recursive functions.

We abuse kwargs to have a pythonic assignment syntax for the bindings. However,
because Python evaluates kwargs in an arbitrary order, this approach **cannot**
support bare variable definitions that depend on each other.

To enforce a particular evaluation order, it is possible to nest let forms,
or to use a different (more lispy than pythonic) syntax that comes with a
particular (specifically, left-to-right) ordering. For the latter, see the
following example on SO (it's actually a somewhat rackety letrec, with
automatic nesting to support let*):
    https://stackoverflow.com/a/44737147

Finally, since we don't depend on MacroPy, we obviously provide everything as
run-of-the-mill functions, not actual syntactic forms.

Inspiration:
    https://nvbn.github.io/2014/09/25/let-statement-in-python/
    https://stackoverflow.com/questions/12219465/is-there-a-python-equivalent-of-the-haskell-let
    http://sigusr2.net/more-about-let-in-python.html

Created on Mon Apr 30 13:51:47 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

class env:
    """Bunch with context manager, iterator and subscripting support.

    Iteration and subscripting just expose the underlying dict.

    Also works as a bare bunch.

    Usage:
        # with context manager:
        with env(x = 0) as myenv:
            print(myenv.x)
        # DANGER: myenv still exists due to Python's scoping rules.

        # bare bunch:
        myenv2 = env(s="hello", orange="fruit", answer=42)
        print(myenv2.s)
        print(myenv2)

        # iteration and subscripting:
        names = [k for k in myenv2]

        for k,v in myenv2.items():
            print("Name {} has value {}".format(k, v))
    """
    def __init__(self, **bindings):
        self._env = {}
        for name,value in bindings.items():
            self._env[name] = value

    # item access by name
    #
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

    # context manager
    #
    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        # we could nuke our *contents* to make all names in the environment
        # disappear, but it's simpler and more predictable not to.
        pass

    # iteration
    #
    def __iter__(self):
        return self._env.__iter__()

    def __next__(self):
        return self._env.__next__()

    def items(self):
        return self._env.items()

    # subscripting
    #
    def __getitem__(self, k):
        return getattr(self, k)

    def __setitem__(self, k, v):
        setattr(self, k, v)

    # pretty-printing
    #
    def __str__(self):
        bindings = ["{}: {}".format(name,value) for name,value in self._env.items()]
        return "<env: <{:s}>>".format(", ".join(bindings))

    # other
    #
    def set(self, name, value):
        """Convenience method to allow assignment in expression contexts.

        Like Scheme's set! function.

        For convenience, returns the `value` argument.
        """
        setattr(self, name, value)
        return value  # for convenience


def letexpr(body, **bindings):
    """let expression, for use with lambdas.

    Examples:

        # order-preserving list uniqifier
        f = lambda lst: letexpr(seen=set(),
                                body=lambda env: [env.seen.add(x) or x for x in lst if x not in env.seen])

        # a lambda that uses a locally defined lambda as a helper
        g = letexpr(square=lambda x: x**2,
                    body=lambda env: lambda x: 42 * env.square(x))
        print(g(10))

    As Lisp programmers know, the second example is subtly different from:

        g = lambda x: letexpr(square=lambda y: y**2,
                              body=lambda env: 42 * env.square(x))

    In the original version, the letexpr runs just once, when g is defined,
    whereas in this one, it re-runs whenever g is called.

    Parameters:
        `body`: one-argument function to run, taking an `env` instance that
                contains the "let" bindings as its attributes.

                To pass in more stuff:
                    - Use the closure property (free variables, lexical scoping)
                    - Make a nested lambda; only the outermost one is implicitly
                      called with env as its only argument.

        Everything else: "let" bindings; each argument name is bound to its value.
        No "lambda env:" is needed, as the environment is not seen by the bindings.

    Returns:
        The value returned by body.
    """
    return body(env(**bindings))


def letrecexpr(body, **bindings):
    """letrec expression, for use with lambdas.

    The bindings have mutually recursive name resolution, like in Scheme.

    In letrecexpr, also the bindings must be wrapped with a "lambda env:",
    to delay their evaluation until the environment instance has been created
    (and can thus be supplied to them).

    In the actual definitions, the names can be used just like any let-defined
    names, as env.*.

    Example:

        t = letrecexpr(evenp=lambda env: lambda x: (x == 0) or env.oddp(x - 1),
                       oddp=lambda env: lambda x: (x != 0) and env.evenp(x - 1),
                       body=lambda env: env.evenp(42))

    Parameters:
        `body`: like in letexpr()

        Everything else: "letrec" bindings, as one-argument functions.
        The argument is the environment.

    Returns:
        The value returned by body.
    """
    # Set up the environment as usual.
    e = env(**bindings)

    # Strip the "lambda env:" from each item, binding its "env"
    # formal parameter to this environment instance itself.
    #
    # Because we only aim to support function (lambda) definitions,
    # it doesn't matter that some of the names used in the definitions
    # might not yet exist in e, because Python only resolves the
    # name lookups at runtime (i.e. when the inner lambda is called).
    #
    for k in e:
        e[k] = e[k](e)

    return body(e)


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


def letrec_over_def(**bindings):
    """letrec decorator, for use with named functions.

    Like let_over_def, but for letrec.
    """
    def deco(body):
        # evaluate env when the function def runs!
        # (so that any mutations to its state are preserved
        #  between calls to the decorated function)
        e = env(**bindings)
        # Supply the environment instance to the letrec bindings.
        for k in e:
            e[k] = e[k](e)
        def decorated(*args, **kwargs):
            kwargs_with_env = kwargs.copy()
            kwargs_with_env["env"] = e
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

    ################################

    # Tangentially related:
    #
    # Python lambdas allow only one body expression, but taking a page from Racket...
    #
    # Let's sequence some operations inside a lambda:

    def begin_lazy(*bodys):
        """Racket-like begin: run bodys in sequence, return the return value of the last one.

        Each body must be a thunk (0-argument function), to delay its evaluation
        until begin() runs.
        """
        *rest,last = bodys
        for body in rest:
            body()
        return last()

    def begin0_lazy(*bodys):
        """Racket-like begin0: run bodys in sequence, return the return value of the *first* one.

        Each body must be a thunk (0-argument function), to delay its evaluation
        until begin0() runs.
        """
        first,*rest = bodys
        out = first()
        for body in rest:
            body()
        return out

    # Even simpler: if we allow Python's eager evaluation of the bodys,
    # we can simply pack the values into a tuple and return the value we want.

    def begin(*vals):   # eager, bodys already evaluated when this is called
        """Racket-like begin: return the last value."""
        return vals[-1]

    def begin0(*vals):  # eager, bodys already evaluated when this is called
        """Racket-like begin0: return the first value."""
        return vals[0]

    test_begin_lazy = lambda: begin_lazy(lambda: print("hi"),
                                         lambda: "return value of begin_lazy")
    test_begin0_lazy = lambda: begin0_lazy(lambda: "return value of begin0_lazy",
                                           lambda: print("hi again"))
    print(test_begin_lazy())
    print(test_begin0_lazy())

    # This is very convenient e.g. for inserting debug prints inside lambdas:

    test_begin = lambda x: begin(print("hi, my argument is {}".format(x)),  # value ignored
                                 "we could do some side effects here",      # value ignored
                                 "I'm the return value of begin")           # value returned
    test_begin0 = lambda: begin0("return value of begin0",
                                 print("hi again"))
    print(test_begin(9001))
    print(test_begin0())

    # Let over lambda, expression version.
    # The inner lambda is the definition of the function f.
    f = letexpr(x = 0,
                body = lambda env: lambda: begin(env.set("x", env.x + 1),
                                                 env.x))
    print(f())
    print(f())
    print(f())

    # https://docs.racket-lang.org/reference/let.html
    t = letrecexpr(evenp=lambda env: lambda x: (x == 0) or env.oddp(x - 1),
                   oddp=lambda env: lambda x: (x != 0) and env.evenp(x - 1),
                   body=lambda env: env.evenp(42))
    print(t)

    @letrec_over_def(evenp=lambda env: lambda x: (x == 0) or env.oddp(x - 1),
                     oddp=lambda env: lambda x: (x != 0) and env.evenp(x - 1))
    def is_even(x, *, env):  # make env passable by name only
        return env.evenp(x)
    print(is_even(23))
