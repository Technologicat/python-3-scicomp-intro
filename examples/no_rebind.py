#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Disallow rebinding, or (in Scheme terms) make define and set! look different.

For defensive programming, to avoid accidentally overwriting existing names.

Usage:

with no_rebind(ilshift_is_rebind=True) as e:
    e.foo = "bar"       # bind yet-unused name, ok

    e.foo <<= "tavern"  # rebind "foo" in e, only allowed if ilshift_is_rebind
                        # is enabled (default off).

    e.foo = "quux"      # NoRebindError, attempting to re-define "foo".

Created on Mon Feb  5 21:57:56 2018

@author: jje
"""

# To be able to create _env, in __setattr__ we must special-case it,
# falling back to default behaviour (which is object.__setattr__,
# hence super().__setattr__).
#
# __getattr__ is never called if standard attribute lookup succeeds,
# so there we don't need a hook for _env (as long as we don't try to
# look up _env before it is created).
#
# __enter__ should "return self" to support the binding form "with ... as ...".
#
# https://docs.python.org/3/reference/datamodel.html#object.__setattr__
# https://docs.python.org/3/reference/datamodel.html#object.__getattr__

class NoRebindError(AttributeError):
    pass

class no_rebind:
    def __init__(self, ilshift_is_rebind=False):
        """Constructor.

        Parameters:
            ilshift_is_rebind: bool
                If True, allow rebinding with syntax ``env.foo <<= newval``
                   ("sending" a new value to ``env.foo``). Note this hides
                   the original __ilshift__ method of all values stored in
                   this environment, and also involves copy-constructing foo
                   in and out of wrapper objects, hence the default is off.
                If False, rebinding is completely disabled.
        """
        self._env = {}      # should be private...
        self._env["_norebind_ilshift"] = ilshift_is_rebind

    def __setattr__(self, name, value):
        if name == "_env":  # ...but this looks clearer with no name mangling.
            return super().__setattr__(name, value)

        env = self._env
        if name not in env:
            if self._env["_norebind_ilshift"]:
                value = self._make_rebindable(value)
            env[name] = value
        elif value.__class__.__name__ == "_wrapper":  # from <<=, allow rebind
            env[name] = value
        else:
            raise NoRebindError("Name '{:s}' already bound".format(name))

    def __getattr__(self, name):
        env = self._env
        if name in env:
            return env[name]
        else:
            raise NoRebindError("Name '{:s}' not bound".format(name))

    def __enter__(self):
        return self

    def __exit__(self, exctype, excvalue, traceback):
        pass

    def _make_rebindable(self, obj):
        assert self._env["_norebind_ilshift"], "only available with ilshift_is_rebind=True"

        # For some types (such as int), __ilshift__ does not exist and cannot be
        # written to. Also __lshift__ is read-only, so it's not a possible syntax either.
        #
        # Hence we wrap obj, just adding an (or overriding the) __ilshift__ method.
        env_instance = self
        class _wrapper(obj.__class__):  # new _wrapper type each time we are called!
            # WARNING: this is a bit unusual; most often custom in-place
            # operators mutate and return self.
            #
            # The actual assignment step is performed by Python, using the
            # return value of __ilshift__ as the new value. env.foo <<= newval
            # essentially translates to env.foo = env.foo.__ilshift__(newval).
            #
            # https://docs.python.org/3/library/operator.html#operator.ilshift
            #
            # Usually in-place operators are just a performance optimization.
            # Python knows how to <<= using just << and =, so **most often**
            # we wouldn't even define __ilshift__ separately. But here it's
            # the sensible thing, since we really just want a syntax for an
            # unrelated feature, and this way obj gets to keep its original "<<".
            #
            # See SO on __iadd__:
            #
            # https://stackoverflow.com/questions/1047021/overriding-in-python-iadd-method
            #
            def __ilshift__(self, newval):
                return env_instance._make_rebindable(unwrap(newval))
        def unwrap(obj):  # find first parent class that is not a _wrapper
            for cls in obj.__class__.__mro__:
                if cls.__name__ != "_wrapper":
                    return cls(obj)  # rebuild obj without wrapper
            assert False, "wrapped value missing in {} {}".format(type(obj), obj)
        return _wrapper(obj)  # rebuild obj with wrapper

# Usage example / unit test
def test():
    with no_rebind(ilshift_is_rebind=True) as e:
        try:
            e.a = 2  # success, empty environment so far
            e.b = 3  # success, different name
            print(e.a, e.b)
        except NoRebindError as err:
            print('Test 1 FAILED: {}'.format(err))
        else:
            print('Test 1 PASSED')

        try:
            e.a = 5  # fail, e.a is already bound
            print(e.a)
        except NoRebindError:
            print('Test 2 PASSED')
        else:
            print('Test 2 FAILED')

        # rebind syntax
        try:
            e.a <<= 42
            print(e.a)
            e.a <<= 2*e.a  # type(newval) is int also in this case
            print(e.a)
            e.a <<= e.b    # but here type(newval) is a _wrapper
            print(e.a)
        except NoRebindError as err:
            print('Test 3 FAILED: {}'.format(err))
        else:
            print('Test 3 PASSED')

        try:
            e.c <<= 3  # fail, e.c not bound
        except NoRebindError as err:
            print('Test 4 PASSED')
        else:
            print('Test 4 FAILED')

if __name__ == '__main__':
    test()
