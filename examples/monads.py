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
operation that does not chain.)

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

##################################
# Some monads
##################################

# No-op monad - just regular function composition.
#
# Useless in practice, but shows the structure in its simplest form.
#
class Noop:
    def __init__(self, x):    # unit: a -> M a
        self.x = x
    def __rshift__(self, f):  # bind: (M a), (a -> M a) -> (M a)
        return f(self.x)
    def __str__(self):
        return "<No-op monad, data value {}>".format(self.x)
    # Lift a regular function into a Noop-producing one.
    @classmethod
    def lift(cls, f):
        return lambda x: cls(f(x))

# Maybe - simple exception handling.
#
# A return value of Maybe(None) is taken to indicate that an error occurred,
# and that the rest of the computation is to be suppressed.
#
# To take the Haskell analogy further, could use MacroPy and case classes
# to approximate an ADT that actually consists of Just and Nothing.
#
class Maybe:
    def __init__(self, x):    # unit: a -> M a
        self.x = x

    def __rshift__(self, f):  # bind: (M a), (a -> M a) -> (M a)
        if self.x is not None:
            return f(self.x)     # f already returns monadic output
        else:
            return self          # Nothing  (here self.x is already None)

    def __str__(self):
        if self.x is not None:
            return "<Just {}>".format(self.x)
        else:
            return "<Nothing>"

    # Lift a regular function into a Maybe-producing one.
    # This is essentially compose(unit, f).
    @classmethod
    def lift(cls, f):
        return lambda x: cls(f(x))

# List - multivalued functions.
#
class List:
    def __init__(self, *elts):  # unit
        self.x = elts

    def __rshift__(self, f):  # bind
        # essentially List(flatmap(lambda i: f(i), self.x))
        return List(*[j for i in self.x for j in f(i)])

    def __getitem__(self, i):  # make List iterable so that f(i) above works
        return self.x[i]

    def __str__(self):
        return "<List {}>".format(self.x)

    # Lift a regular function into a List-producing one.
    @classmethod
    def lift(cls, f):
        return lambda x: cls(f(x))

# Writer - debug logging.
#
class Writer:
    def __init__(self, x, log=""):
        self.data = (x, log)

    def __rshift__(self, f):
        x0, log = self.data
        x1, msg = f(x0).data
        return Writer(x1, log + msg)

    def __str__(self):
        return "<Writer {}>".format(self.data)

    # Lift a regular function into a debuggable one.
    # http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html
    @classmethod
    def lift(cls, f):
        return lambda x: cls(f(x), "[{} was called on {}]".format(f, x))


##################################
# Some monadic functions
##################################

def noop_sqrt(x):   # a -> Noop a
    return Noop(x**0.5)

# real-valued square root: fail for x < 0
def maybe_sqrt(x):  # a -> Maybe a
    if x >= 0:
        return Maybe(x**0.5)  # Just ...
    else:
        return Maybe(None)    # Nothing

# multivalued square root (for reals)
def multi_sqrt(x):  # a -> List a
   if x < 0:
       return List()
   elif x == 0:
       return List(0)
   else:
       return List(x**0.5, -x**0.5)

# debug-logging square root
def writer_sqrt(x): # a -> Writer a
    return Writer(x**0.5, "[sqrt was called for {}]".format(x))


##################################
# Main program
##################################

def main():
    # Noop: regular function composition.
    #
    n = Noop(4)
    print(n >> noop_sqrt >> noop_sqrt)

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

    # List: compose functions that may return multiple answers
    #
    l = List(5, 0, 3)
    print(l >> multi_sqrt >> multi_sqrt)

    l = List(4)
    print(l >> multi_sqrt >> multi_sqrt)

    l = List(4)
    print(l >> multi_sqrt >> List.lift(div2) >> multi_sqrt)

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

if __name__ == '__main__':
    main()
