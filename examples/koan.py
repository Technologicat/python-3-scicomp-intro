#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A pythonic koan on objects and closures.

For the original discussion that inspired this example, see:
    http://people.csail.mit.edu/gregs/ll1-discuss-archive-html/msg03277.html
"""

# Objects and closures are in a sense dual.
#
# Objects are a poor man's closures:

def make_adder(a):  # essentially __init__
    def adder(x):   # essentially __call__
        return x + a
    return adder

class Adder:
    def __init__(self, a):
        self.a = a
    def __call__(self, x):
        return self.a + x

f1 = make_adder(17)
assert f1(25) == 42

f2 = Adder(17)
assert f2(25) == 42

# So if all you need is a __call__ method and some per-instance data,
# maybe consider a closure; fewer syntactic elements, more readable.
#
# But what if you need more methods than just __call__?
# Closures are a poor man's objects:

class Thing:
    """A thing."""
    c = 17
    def __init__(self, a):
        self.a = a
    def addthem(self):
        return self.a + self.c
    def multiplythem(self):
        return self.a * self.c

def make_thing_type(c):
    """Construct the class, binding class attributes. Return the instance constructor."""
    def make(a):
        """Essentially __init__."""
        # instance methods
        def addthem():
            return a + c
        def multiplythem():
            return a * c

        # Method lookup.
        #
        # We cheat a little, assuming the bindings of the locals don't change
        # during the lifetime of the object (since creating the dictionary can be expensive).
        # (If we don't care about that, we could just ask for it every time inside instancedispatch.)
        _data = locals()
        def instancedispatch(name, *args, **kwargs):
            """A thing, represented as a closure.

            ``name`` is the name of the method to call; ``*args`` and ``**kwargs``
            are passed through to it.
            """
            try:
                f = _data[name]
            except KeyError as err:
                raise AttributeError("'{}' is not a member of this instance".format(name)) from err
            if not callable(f):
                raise TypeError("'{}' is not a method of this instance".format(name))
            return _data[name](*args, **kwargs)
        return instancedispatch
    return make
Thing2 = make_thing_type(17)

t1 = Thing(25)
assert t1.addthem() == 42
assert t1.multiplythem() == 17 * 25

t2 = Thing2(25)
assert t2("addthem") == 42
assert t2("multiplythem") == 17 * 25

# test error handling
try:
    t2("c")
except TypeError:
    pass
else:
    assert False

try:
    t2("some_nonexistent_method")
except AttributeError:
    pass
else:
    assert False

# -----------------------------------------------------------------------------
# Advanced.
#
# If we want to be a bit fancier, allowing class methods to be called
# on both an instance and directly on the class...

def make_otherthing_type(c):
    """Construct the class, binding class attributes. Return the class-level dispatcher.

    The class method ``make`` is the instance constructor.
    """
    # class methods
    def hello():
        return "hello"
    def get_c():
        return c
    def set_c(value):
        nonlocal c
        c = value
    def make(a):
        """Essentially __init__."""
        # instance methods
        def addthem():
            return a + c
        def multiplythem():
            return a * c

        _data = locals()
        def instancedispatch(name, *args, **kwargs):
            """A thing."""
            try:
                f = _data[name]
            except KeyError as err:
                return classdispatch(name, *args, **kwargs)
            if not callable(f):
                raise TypeError("'{}' is not a method of this instance".format(name))
            return _data[name](*args, **kwargs)
        return instancedispatch

    _data = locals()
    def classdispatch(name, *args, **kwargs):
        """Type for a thing. Dispatch to ``make`` to create an instance."""
        try:
            f = _data[name]
        except KeyError as err:
            raise AttributeError("'{}' is not a member of this class".format(name)) from err
        if not callable(f):
            raise TypeError("'{}' is not a method of this class".format(name))
        return _data[name](*args, **kwargs)
    return classdispatch
Thing3 = make_otherthing_type(17)

# Now the constructor call looks a bit different...
t3 = Thing3("make", 25)

# ...and we can call both class and instance methods on an instance.
assert t3("hello") == "hello"
assert t3("get_c") == 17
t3("set_c", 23)
assert t3("get_c") == 23
assert t3("addthem") == 23 + 25
assert t3("multiplythem") == 23 * 25

t4 = Thing3("make", 32)
assert t4("get_c") == 23         # the same ``c`` is shared between instances
assert t4("addthem") == 23 + 32  # and each instance has its own ``a``
assert t4("multiplythem") == 23 * 32

# Naturally, calling class methods directly on the class works, too.
assert Thing3("get_c") == 23

# ...and trying to call an instance method on the class is an AttributeError.
try:
    Thing3("addthem")
except AttributeError:
    pass
else:
    assert False

# Of course, even this doesn't yet cover everyday features of Python's classes
# such as inheritance, properties, or being able to inject new attributes
# (for this, an explicit dictionary to store them would be better than storing
# them in function locals directly), and this doesn't support easy introspection.
#
# Hence **poor man's objects**.
#
# It's possible to build at least most of that, but there's no point, since Python
# already has an object system that does all of this.
#
# But if one day all you have is a minimal Lisp without objects, this is the
# basic idea behind how to create an object system (and then package the whole
# thing as macros to eliminate the boilerplate).
