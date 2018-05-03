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

# Currently unused, left in for documentation purposes only.
#def isiterable(x):
#    # Duck test the input for iterability.
#    # We only try making a generator, so the test should be fast.
#    # https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
#    try:
#        (elt for elt in x)
#        return True
#    except TypeError:
#        return False
#    assert False, "can't happen"

##################################
# Some monads
##################################

# Helper singleton data value, to be compared using "is"
#
Empty = []  # Any mutable, to get an instance distinct from any other object.
            # We won't actually mutate its state.
            # (Slightly hackish; in Lisps, we could instead define a symbol.)

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
        if not isinstance(self.x, Identity):
            raise TypeError("Expected a nested Identity monad, got {} with data {}".format(type(self.x), self.x))
        return self.x

# Maybe - simple error handling.
#
# A return value of Maybe(Empty) is taken to indicate that an error occurred,
# and that the rest of the computation is to be skipped.
#
# The magic is that the calling code needs no if/elses checking for an
# error return value - those are refactored into this monad.
#
# To take the Haskell analogy further, we could use MacroPy and case classes
# to approximate an ADT that actually consists of Just and Nothing.
#
# Instead, here:
#   - Nothing is represented as Maybe(Empty), and
#   - Just x is represented as Maybe(x).
#
class Maybe:
    def __init__(self, x):    # unit: x: a -> M a
        self.x = x

    def __rshift__(self, f):  # bind: x: (M a), f: (a -> M b) -> (M b)
        # bind ma f = join (fmap f ma)
        return self.fmap(f).join()
        # manual implementation of bind
#        if self.x is Empty:
#            return self
#        else:
#            return f(self.x)     # this f already returns monadic output

    def __str__(self):
        if self.x is Empty:
            return "<Nothing>"
        else:
            return "<Just {}>".format(self.x)

    # Lift a regular function into a Maybe-producing one.
    # This is essentially compose(unit, f).
    @classmethod
    def lift(cls, f):         # lift: f: (a -> b) -> (a -> M b)
        return lambda x: cls(f(x))

    # http://learnyouahaskell.com/functors-applicative-functors-and-monoids
    def fmap(self, f):        # fmap: x: (M a), f: (a -> b) -> (M b)
        if self.x is Empty:
            return self
        else:
            return Maybe(f(self.x))

    def join(self):           # join: x: M (M a) -> M a
        if not isinstance(self.x, Maybe) and self.x is not Empty:
            raise TypeError("Expected a nested Maybe monad, got {} with data {}".format(type(self.x), self.x))
        # a maybe of a maybe - unwrap one layer
        if self.x is Empty:
            return self
        else:
            return self.x

# List - multivalued functions.
#
class List:
    def __init__(self, *elts):  # unit: x: a -> M a
        # For convenience with liftm2 (see further below): accept Empty
        # as a special *item* that, when passed to the List constructor,
        # produces an empty list.
        #
        # (The issue is that the standard liftm2 takes a regular function,
        #  where the output is just one item; the construction of the
        #  List container for this item occurs inside liftm2. Hence,
        #  the special meaning "no result" must be encoded somehow.)
        #
        if len(elts) == 1 and elts[0] is Empty:
            self.x = ()
        else:
            self.x = elts

    def __rshift__(self, f):  # bind: x: (M a), f: (a -> M b) -> (M b)
        # bind ma f = join (fmap f ma)
        return self.fmap(f).join()
        # done manually, essentially List.from_iterable(flatmap(lambda elt: f(elt), self.x))
        #return List.from_iterable(result for elt in self.x for result in f(elt))

    def __getitem__(self, i): # make List iterable so that "for result in f(elt)" works
        return self.x[i]      # (when f outputs a List monad)

    def __add__(self, other): # concatenation of Lists, for convenience
        return List.from_iterable(self.x + other.x)

    def __str__(self):
        return "<List {}>".format(self.x)

    @classmethod
    def from_iterable(cls, iterable):  # convenience
        try:
            return cls(*iterable)
        except TypeError: # maybe a generator; try forcing it before giving up.
            return cls(*tuple(iterable))

    def copy(self):
        return List(*self.x)

    # Lift a regular function into a List-producing one.
    @classmethod
    def lift(cls, f):         # lift: f: (a -> b) -> (a -> M b)
        return lambda x: cls(f(x))

    def fmap(self, f):        # fmap: x: (M a), f: (a -> b) -> (M b)
        return List.from_iterable(f(elt) for elt in self.x)

    def join(self):           # join: x: M (M a) -> M a
        if not all(isinstance(elt, List) for elt in self.x):
            raise TypeError("Expected a nested List monad, got {}".format(self.x))
        # list of lists - concat them
        return List.from_iterable(elt for sublist in self.x for elt in sublist)

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
        if not isinstance(self.data, Writer):
            raise TypeError("Expected a nested Writer monad, got {} with data {}".format(type(self.data), self.data))
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
        return Maybe(Empty)   # Nothing

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
    l = List(5, 0, 3)
    print(l >> multi_sqrt >> multi_sqrt)

    l = List(4)
    print(l >> multi_sqrt >> multi_sqrt)

    l = List(4)
    print(l >> multi_sqrt >> List.lift(div2) >> multi_sqrt)

    l = List(5, 0, 3)
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
    def make_maybe_binary_op(proc):   # proc: (c, d) -> e
        def maybe_binary_op(Mx, My):  # Mx: Maybe c,  My: Maybe d
            return Mx >> (lambda a: My >> (lambda b: Maybe(proc(a, b))))
        return maybe_binary_op

    add = lambda x,y: x + y
    maybe_add = make_maybe_binary_op(add)
    print(maybe_add(Maybe("Hello, "), Maybe("world!")))

    # Alternative (perhaps silly) way - encode multiple arguments into a tuple
    # (which is then the single data item inside the Maybe):
    #
    tadd = lambda x_and_y: add(*x_and_y)
    maybe_add2 = lambda M_x_and_y: M_x_and_y.fmap(tadd)
    print(maybe_add2(Maybe(("Hello, ", "world!"))))  # extra parens to create tuple

    # Abstracting the previous solution further: "liftm2".
    #
    # Note the slight asymmetry between liftm2 and lift:
    #
    #   lift:    f: (a -> b)       ->  lifted: (a -> M b)
    #   liftm2:  f: ((c, d) -> e)  ->  lifted: ((M c, M d) -> M e)
    #
    # Why the Ms in the input in liftm2? This is because in liftm2 the *lifted*
    # function binds, whereas lift expects the use site to do that.
    #
    # Note that Haskell defines liftm3, liftm4, ... liftm8 similarly. E.g.
    #
    #   liftm3:  f: ((c, d, e) -> r)  ->  lifted: ((M c, M d, M e) -> M r)
    #
    def liftm2(M, f): # M: monad type,  f: ((c, d) -> e)  ->  lifted: ((M c, M d) -> M e)
        def lifted(Mx, My):
            if not isinstance(Mx, M):
                raise TypeError("first argument: expected monad {}, got {} with data {}".format(M, type(Mx), Mx))
            if not isinstance(My, M):
                raise TypeError("second argument: expected monad {}, got {} with data {}".format(M, type(My), My))
            return Mx >> (lambda a: My >> (lambda b: M(f(a, b))))
        return lifted

    # Cartesian product of two lists:
    #
    concat = add  # for lists, + means concatenation; let's just be explicit with terminology.
    list_prod = liftm2(List, concat)
    print(list_prod(List("Hello", "Hi"), List(" there!", " everyone!")))
    print(list_prod(List((1, 2), (3, 4)), List((10, 20), (30, 40))))

    # DANGER: since + is overloaded in Python, it will also happily sum numbers:
    print(list_prod(List(1, 2), List(10, 20)))

    # Not to be confused with direct concatenation of lists:
    print(List(1, 2, 3) + List(4, 5, 6))

    # Trying to use the other solution from the Maybe example here
    # *doesn't* work, because of the structure of what we want to do.
    #
    # This just concatenates each input list, provided it has two items (exercise: why?).
    #
    list_prod_borked = lambda M_x_and_y: M_x_and_y.fmap(tadd)
    print(list_prod_borked(List(("Hello", "Hi"), (" there!", " everyone!"))))

    # (As to the exercise, maybe considering this helps?)
    #
    def m1_concat(Mx, My):
        # My is the whole second list, whereas a is an item from Mx (the first list).
        return Mx.fmap(lambda a: (a,) + My.x)  # we must .x to get to the tuple inside.
    print(m1_concat(List("Hello", "Hi"), List(" there!", " everyone!")))

    def div(x, y):  # (a, a) -> a or no result
        if y != 0:
            return x / y
        else:
            return Empty  # Suppress output if division by zero.
                          #
                          # Hence, failed branches of the computation
                          # automatically disappear from the results.
                          #
                          # This is the same trick we used with
                          # generators to produce only successful
                          # anagrams (exercises 3, question 7);
                          # an empty output list causes automatic backtracking.
    list_div = liftm2(List, div)
    print(list_div(List(0, 1, 2, 3), List(0, 1, 2, 3)))

    # Alternative way:
    #
    print(List(10, 20, 30, 40) >> (lambda a:
          List(0, 1, 2, 3)     >> (lambda b:
          List(a / b) if b != 0 else List())))  # Here we don't need Empty.
                                                # We output a monad:
                                                #   (a, a) -> M a
                                                # since we don't need to
                                                # conform to the API of liftm2.


    # Another use for List - nondetermistic evaluation.
    #
    # Essentially, we just make a cartesian product, like above...
    print(List(3, 10, 6) >> (lambda a:  # semantically, these are now lists of possible choices
          List(100, 200) >> (lambda b:
          List(a + b))))

    # ...but this becomes interesting when we add a filter.
    is_even = lambda x: List(x) if x % 2 == 0 else List()
    print(List(4, 5)   >> (lambda a:
          List(11, 14) >> (lambda b:
          List(a + b)))
          >> is_even)

    # find pythagorean triples
    A = List.from_iterable(range(1, 21))
    B = A.copy()
    C = A.copy()
    pt = A >> (lambda a:
         B >> (lambda b:
         C >> (lambda c:
         List((a,b,c)) if a*a + b*b == c*c else List())))
    # accept only sorted entries
    pts = pt >> (lambda t: List(t) if t[0] < t[1] < t[2] else List())
    print(pts)

if __name__ == '__main__':
    main()
