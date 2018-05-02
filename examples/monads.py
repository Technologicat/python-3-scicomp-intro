#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Some simple monad examples in Python.

A monad is really just a design pattern, that can be described as:
  - chaining of operations with custom processing between steps, or
  - generalization of function composition.

Examples heavily based on these posts by Stephan Boyer (2012):

  https://www.stephanboyer.com/post/9/monads-part-1-a-design-pattern
  https://www.stephanboyer.com/post/10/monads-part-2-impure-computations

We give an OOP-ish version - the constructor for each monad class plays the
role of unit(), and bind is spelled as ">>" (via __rshift__). (In Python,
the standard bind symbol ">>=" is used for __irshift__, which is an in-place
operation that does not chain, so we can't use that.)

The general pattern is: monad-wrap an initial value with unit(), then send it
to a sequence of monadic functions with bind. Each function in the chain must
use the same type of monad for this to work. See examples below.

See also these approachable explanations:

  http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html
  https://stackoverflow.com/questions/44965/what-is-a-monad

Further reading:

  http://www.valuedlessons.com/2008/01/monads-in-python-with-nice-syntax.html
  https://github.com/dbrattli/OSlash
  https://bitbucket.org/jason_delaat/pymonad/
  https://github.com/dpiponi/Monad-Python

Created on Tue May  1 00:25:16 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

def isiterable(x):
    # Duck test the input for iterability.
    # We only try making a generator, so the test should be fast.
    # https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
    try:
        _ = (elt for elt in x)
        return True
    except TypeError:
        return False
    assert False, "can't happen"

##################################
# Some monads
##################################

# Identity monad (cf. identity function) - no-op, just regular function composition.
#
# Shows the structure in its simplest form.
#
class Identity:
    def __init__(self, x):    # unit: x: a -> M a
        self.x = x
    def __rshift__(self, f):  # bind: x: (M a), f: (a -> M b) -> (M b)
        # bind ma f = join (fmap f ma)
        return self.fmap(f).join()
        # manual implementation of bind
#        return f(self.x)
    def __str__(self):
        return "<Identity {}>".format(self.x)
    # Lift a regular function into an Identity monad producing one.
    @classmethod
    def lift(cls, f):         # lift: f: (a -> b) -> (a -> M b)
        return lambda x: cls(f(x))
    # http://learnyouahaskell.com/functors-applicative-functors-and-monoids
    def fmap(self, f):        # fmap: x: (M a), f: (a -> b) -> (M b)
        return Identity(f(self.x))
    def join(self):           # join: x: M (M a) -> M a
        return self.x

# Maybe - simple error handling.
#
# A return value of Maybe(None) is taken to indicate that an error occurred,
# and that the rest of the computation is to be skipped.
#
# The magic is that the calling code needs no if/elses checking for an
# error return value - those are refactored into this monad.
#
# To take the Haskell analogy further, we could use MacroPy and case classes
# to approximate an ADT that actually consists of Just and Nothing.
#
# Instead, here Nothing is represented as Maybe(None),
# and Just x is represented as Maybe(x).
#
class Maybe:
    def __init__(self, x):    # unit: x: a -> M a
        self.x = x

    def __rshift__(self, f):  # bind: x: (M a), f: (a -> M b) -> (M b)
        # bind ma f = join (fmap f ma)
        return self.fmap(f).join()
        # manual implementation of bind
#        if self.x is not None:
#            return f(self.x)     # this f already returns monadic output
#        else:
#            return self          # Nothing  (here self.x is already None)

    def __str__(self):
        if self.x is not None:
            return "<Just {}>".format(self.x)
        else:
            return "<Nothing>"

    # Lift a regular function into a Maybe-producing one.
    # This is essentially compose(unit, f).
    @classmethod
    def lift(cls, f):         # lift: f: (a -> b) -> (a -> M b)
        return lambda x: cls(f(x))

    # http://learnyouahaskell.com/functors-applicative-functors-and-monoids
    def fmap(self, f):        # fmap: x: (M a), f: (a -> b) -> (M b)
        if self.x is not None:
            return Maybe(f(self.x))
        else:
            return self  # Nothing

    def join(self):           # join: x: M (M a) -> M a
        if not isinstance(self.x, Maybe) and self.x is not None:
            raise TypeError("expected Maybe, got '{}'".format(type(self.x)))
        # a maybe of a maybe - unwrap one layer
        if self.x is not None:
            return self.x
        else:
            return self  # Nothing

# List - multivalued functions.
#
class List:
    # tuple-like API - elts must be just one iterable.
    def __init__(self, elts):  # unit: x: a -> M a
        if not isiterable(elts):
            raise TypeError("Expected an iterable, got '{}'".format(type(elts)))
        self.x = tuple(elts)

    # convenience, e.g. List.pack(1, 2, 3) vs. List((1, 2, 3))
    @classmethod
    def pack(cls, *elts):
        return cls(elts)

    def __rshift__(self, f):  # bind: x: (M a), f: (a -> M b) -> (M b)
        # bind ma f = join (fmap f ma)
        return self.fmap(f).join()
        # done manually, essentially List(flatmap(lambda elt: f(elt), self.x))
        #return List([result for elt in self.x for result in f(elt)])

    def __getitem__(self, i): # make List iterable so that f(i) above works
        return self.x[i]      # (f outputs a List monad)

    def __add__(self, other): # concatenation of Lists, for convenience
        # essentially List(append(self, other))
        return List([elt for elts in (self.x, other.x) for elt in elts])

    def __str__(self):
        return "<List {}>".format(self.x)

    def copy(self):
        return List(self.x)

    # Lift a regular function into a List-producing one.
    @classmethod
    def lift(cls, f):         # lift: f: (a -> b) -> (a -> M b)
        return lambda x: cls.pack(f(x))

    def fmap(self, f):        # fmap: x: (M a), f: (a -> b) -> (M b)
        return List([f(elt) for elt in self.x])

    def join(self):           # join: x: M (M a) -> M a
        if not isiterable(self.x):
            raise TypeError("Expected an iterable, got '{}'".format(type(self.x)))
        # list of lists - concat them
        return List(elt for sublist in self.x for elt in sublist)

# Writer - debug logging.
#
class Writer:
    def __init__(self, x, log=""):  # unit: x: a -> M a
        self.data = (x, log)

    def __rshift__(self, f):        # bind: x: (M a), f: (a -> M b) -> (M b)
        # works but causes extra verbosity in log, since fmap also logs itself.
#        return self.fmap(f).join()
        # so let's do this one manually.
        x0, log = self.data
        x1, msg = f(x0).data
        return Writer(x1, log + msg)

    def __str__(self):
        return "<Writer {}>".format(self.data)

    # Lift a regular function into a debuggable one.
    # http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html
    @classmethod
    def lift(cls, f):               # lift: f: (a -> b) -> (a -> M b)
        return lambda x: cls(f(x), "[{} was called on {}]".format(f, x))

    def fmap(self, f):              # fmap: x: (M a), f: (a -> b) -> (M b)
        x0, log = self.data
        x1      = f(x0)
        msg     = "[fmap was called with {} on {}]".format(f, x0)
        return Writer(x1, log + msg)

    def join(self):                 # join: x: M (M a) -> M a
        (x, inner_log), outer_log = self.data
        return Writer(x, outer_log + inner_log)


##################################
# Some monadic functions
##################################

# Manual dispatch - just a bunch of functions, caller has to be careful
# to use the correct version (the one for the monad type used by caller).
#
# Implementing automatic dispatch is trickier than usual, since the input
# is always just an "a" - we would have to switch on the *desired output type*,
# which depends on which monad type called us.
#
# Could be implemented by an operation table (each monad type knows which
# version it wants to call), or an extra parameter (each monad type knows
# who it itself is; pass self into f, and let the implementation isinstance()
# on that and do the dispatching, as usual in dynamically typed languages).

def sqrt(x):  # regular function, a -> a
    return x**0.5

def id_sqrt(x):   # a -> Identity a
    return Identity(x**0.5)

# real-valued square root: fail for x < 0
def maybe_sqrt(x):  # a -> Maybe a
    if x >= 0:
        return Maybe(x**0.5)  # Just ...
    else:
        return Maybe(None)    # Nothing

# multivalued square root (for reals)
def multi_sqrt(x):  # a -> List a
   if x < 0:
       return List.pack()
   elif x == 0:
       return List.pack(0)
   else:
       return List.pack(x**0.5, -x**0.5)

# debug-logging square root
def writer_sqrt(x): # a -> Writer a
    return Writer(x**0.5, "[sqrt was called on {}]".format(x))


##################################
# Main program
##################################

def main():
    ########################################################################
    # Identity: regular function composition.
    #
    print(Identity(4) >> id_sqrt >> id_sqrt)

    ########################################################################
    # Maybe: compose functions that may raise an exception
    #
    m = Maybe(256)
    print(m >> maybe_sqrt >> maybe_sqrt >> maybe_sqrt)

    m = Maybe(-256)
    print(m >> maybe_sqrt >> maybe_sqrt >> maybe_sqrt)

    # Via lifting, we can also use regular functions in the chain:
    def div2(x):
        return x / 2
    m = Maybe(256)
    print(m >> maybe_sqrt >> maybe_sqrt >> Maybe.lift(div2) >> maybe_sqrt)

    # We can also map a regular function over the monad via fmap:
    print(m.fmap(sqrt))

    ########################################################################
    # List: compose functions that may return multiple answers
    #
    l = List.pack(5, 0, 3)
    print(l >> multi_sqrt >> multi_sqrt)

    l = List.pack(4)
    print(l >> multi_sqrt >> multi_sqrt)

    l = List.pack(4)
    print(l >> multi_sqrt >> List.lift(div2) >> multi_sqrt)

    l = List.pack(5, 0, 3)
    print(l.fmap(sqrt))

    ########################################################################
    # Writer: compose functions that return also debug messages
    #
    def u(x):  # x -> Writer x
        return Writer(x + 4, "[u was called on {}]".format(x))
    def v(x):
        return Writer(x * 2, "[v was called on {}]".format(x))
    def w(x):  # regular function, no logging!
        return x - 1
    print(Writer(4) >> v >> u >> Writer.lift(w))
    print(Writer(4) >> writer_sqrt)

    print(Writer(4).fmap(sqrt))

    ########################################################################
    # How to handle operations that take more than one argument - curry!
    #
    print(Maybe("Hello, ") >> (lambda a: Maybe("world!") >> (lambda b: Maybe(a + b))))

    # Making that into a function:
    #
    def maybe_add_v1(x, y):
        return Maybe(x) >> (lambda a: Maybe(y) >> (lambda b: Maybe(a + b)))
    print(maybe_add_v1("Hello, ", "world!"))

    # Or in other words (though here lambdas may look more readable?):
    #
    def maybe_add_v2(x, y):
        def outer(a):                # curry x
            def inner(b):            # curry y
                return Maybe(a + b)  # evaluate
            return Maybe(y) >> inner
        return Maybe(x) >> outer
    print(maybe_add_v2("Hello, ", "world!"))

    # Abstracting this pattern:
    #
    def make_maybe_binary_op(proc):  # proc: (c, c) -> Maybe d
        def maybe_binary_op(x, y):
            return Maybe(x) >> (lambda a: Maybe(y) >> (lambda b: proc(a, b)))
        return maybe_binary_op

    add  = lambda x,y: x + y
    madd = lambda x,y: Maybe(add(x, y))
    maybe_add = make_maybe_binary_op(madd)
    print(maybe_add("Hello, ", "world!"))

    # Alternative way - encode multiple arguments into a tuple
    # (which is then the single data item inside the Maybe):
    #
    tadd = lambda x_and_y: add(*x_and_y)
    maybe_add2 = lambda x_and_y: Maybe(x_and_y).fmap(tadd)
    print(maybe_add2(("Hello, ", "world!")))  # extra parens to create tuple

    # Abstracting the previous solution further:
    #
    def make_monadic_binary_op(m, proc):  # proc: (c, c) -> M d
        def monadic_binary_op(x, y):
            return m(x) >> (lambda a: m(y) >> (lambda b: proc(a, b)))
        return monadic_binary_op

    # Cartesian product of two lists:
    #
    ladd = lambda x,y: List.pack(add(x, y))
    list_add = make_monadic_binary_op(List, ladd)
    print(list_add(("Hello", "Hi"), (" there!", " everyone!")))
    print(list_add((1, 2), (10, 20)))  # add numbers
    print(list_add(((1, 2), (3, 4)), ((10, 20), (30, 40))))  # concat tuples

    # Not to be confused with direct concatenation of lists:
    print(List.pack(1, 2, 3) + List.pack(4, 5, 6))

    # This one *doesn't* work, because of the structure of what we want to do.
    #
    # (Exercise: what is the critical difference between the Maybe example
    #  and this one?)
    #
    list_add_borked = lambda x_and_y: List(x_and_y).fmap(tadd)
    print(list_add_borked((("Hello", "Hi"), (" there!", " everyone!"))))

    # (As to the exercise, maybe considering this helps?)
    #
    def make_foo(m):
        def foo(x, y):
            # y is the whole second list, whereas a is an item from x (the first list).
            return m(x).fmap(lambda a: ((a,) + y))
        return foo
    m1_add = make_foo(List)
    print(m1_add(("Hello", "Hi"), (" there!", " everyone!")))

    def ldiv(x, y):
        if y != 0:
            return List.pack(x / y)
        else:
            return List.pack()  # Suppress output if division by zero.
                                #
                                # Hence, failed branches of the computation
                                # automatically disappear from the results.
                                #
                                # This is the same trick we used with
                                # generators to produce only successful
                                # anagrams (exercises 3, question 7).
    list_div = make_monadic_binary_op(List, ldiv)
    print(list_div((0, 1, 2, 3), (0, 1, 2, 3)))

    # Another use for List - nondetermistic evaluation.
    #
    # Essentially, we just make a cartesian product, like above...
    print(List.pack(3, 10, 6) >> (lambda a:
          List.pack(100, 200) >> (lambda b:
          List.pack(a + b))))

    # ...but this becomes interesting when we add a filter.
    EmptyList = List.pack()
    is_even = lambda x: List.pack(x) if x % 2 == 0 else EmptyList
    print(List.pack(4, 5)   >> (lambda a:
          List.pack(11, 14) >> (lambda b:
          List.pack(a + b)))
          >> is_even)

    # find pythagorean triples
    A = List(range(1, 21))
    B = A.copy()
    C = A.copy()
    pt = A >> (lambda a:
         B >> (lambda b:
         C >> (lambda c:
         List.pack((a,b,c)) if a*a + b*b == c*c else EmptyList)))
    # accept only sorted entries
    pts = pt >> (lambda t: List.pack(t) if t[0] < t[1] < t[2] else EmptyList)
    print(pts)

if __name__ == '__main__':
    main()
