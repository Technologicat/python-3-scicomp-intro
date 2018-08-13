#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Some simple monad examples in Python.

A monad is really just a design pattern, that can be described as:
  - chaining of operations with custom processing between steps, or
  - generalization of function composition.

The approach is based on these posts by Stephan Boyer (2012):

  https://www.stephanboyer.com/post/9/monads-part-1-a-design-pattern
  https://www.stephanboyer.com/post/10/monads-part-2-impure-computations

We give an OO(F)P-ish version - the constructor for each monad class plays the
role of unit(), and bind is spelled as ">>" (via __rshift__). (In Python,
the standard bind symbol ">>=" is used for __irshift__, which is an in-place
operation that does not chain, so we can't use that.)

The general pattern is: monad-wrap an initial value with unit(), then send it
to a sequence of monadic functions with bind. Each function in the chain must
use the same type of monad for this to work. See examples below.

Look especially at the Maybe and List monads; they are perhaps the
most important ones to understand first.

See also these approachable explanations:

  http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html
  http://nikgrozev.com/2013/12/10/monads-in-15-minutes/
  https://stackoverflow.com/questions/44965/what-is-a-monad
  https://www.stephanboyer.com/post/83/super-quick-intro-to-monads

Further reading:

  https://github.com/dbrattli/OSlash
  https://github.com/justanr/pynads
  https://bitbucket.org/jason_delaat/pymonad/
  https://github.com/dpiponi/Monad-Python
  http://www.valuedlessons.com/2008/01/monads-in-python-with-nice-syntax.html

Created on Tue May  1 00:25:16 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

from functools import wraps

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

# Helper singleton data value, to be compared using "is".
# Any mutable, to get an instance distinct from any other object.
#
class Empty:  # sentinel, could be any object but we want a nice __repr__.
    def __repr__(self):
        return "<Empty>"
Empty = Empty()  # create an instance and prevent creating any more of them

###########################################
# Helper functions for working with monads
###########################################

# In what follows, note the slight difference between "liftm" here,
# and "lift" to be introduced later:
#
#   lift:    f: (a -> r)       ->  lifted: (a -> M r)
#   liftm:   f: (a -> r)       ->  lifted: (M a -> M r)
#
# (These are type signatures; each letter stands for a type such as int, str, ....
#  For example, f: (a -> r) means that 'f' is a function that takes a single
#  input parameter of type 'a', and its return value is of type 'r'.
#  "M a" roughly means "monad for data values of type 'a'".)
#
# Why the M in the input in the result of liftm? This is because in liftm,
# the *lifted* function binds, whereas lift expects the use site to do that.
#
# Note that Haskell defines liftm2, liftm3, liftm4, ... liftm8 similarly. E.g.
#
#   liftm2:  f: ((a, b) -> r)     ->  lifted: ((M a, M b) -> M r)
#   liftm3:  f: ((a, b, c) -> r)  ->  lifted: ((M a, M b, M c) -> M r)
#
# In the examples to follow, we'll need just liftm and liftm2.
#
# Don't mind if none of this makes any sense at this point - first look at the
# rest of the code, which is really more important, and return to this detail later.
#
# We're just putting these here so that Python runs their definitions first,
# because we'll be using them.

def liftm(M, f):
    @wraps(f)
    def lifted(Mx):
        if not isinstance(Mx, M):
            raise TypeError("argument: expected monad {}, got {} with data {}".format(M, type(Mx), Mx))
        return Mx >> (lambda x:
                        M(f(x)))
    return lifted

def liftm2(M, f):
    @wraps(f)
    def lifted(Mx, My):
        if not isinstance(Mx, M):
            raise TypeError("first argument: expected monad {}, got {} with data {}".format(M, type(Mx), Mx))
        if not isinstance(My, M):
            raise TypeError("second argument: expected monad {}, got {} with data {}".format(M, type(My), My))
        return Mx >> (lambda x:
               My >> (lambda y:
                        M(f(x, y))))
    return lifted

def liftm3(M, f):
    @wraps(f)
    def lifted(Mx, My, Mz):
        if not isinstance(Mx, M):
            raise TypeError("first argument: expected monad {}, got {} with data {}".format(M, type(Mx), Mx))
        if not isinstance(My, M):
            raise TypeError("second argument: expected monad {}, got {} with data {}".format(M, type(My), My))
        if not isinstance(Mz, M):
            raise TypeError("third argument: expected monad {}, got {} with data {}".format(M, type(Mz), Mz))
        return Mx >> (lambda x:
               My >> (lambda y:
               Mz >> (lambda z:
                        M(f(x, y, z)))))
    return lifted

# Advanced: do notation
#
# This would be most natural to implement as a syntactic macro.
# We use a code generator instead, to stay within Python's builtin
# capabilities.
#
# The price is the sprinkling of "lambda e: ..."s to feed in the environment,
# and manually simulated lexical scoping for env attrs instead of just
# borrowing Python's for run-of-the-mill names.
#
def let(**binding):
    """Like Haskell's <- operator in do notation.

    This is one line for the do notation; there must be exactly one binding,
    written in the kwargs syntax.

    Haskell::

        a <- [1, 2, 3]

    Python::

        let(a=List(1, 2, 3))

    which is just syntactic sugar for::

        ("a", List(1, 2, 3))
    """
    if len(binding) != 1:
        raise ValueError("Expected exactly one binding, got {:d} with values {}".format(len(binding), binding))
    for k, v in binding.items():  # just one but we don't know its name
        return (k, v)

def do(*lines):
    """Monadic **do notation** for Python.

    This is a bit like let* in Lisps, but e.g. with the List monad, each name
    takes on multiple values, and the final results are combined to a single list;
    with the flatmapping implicit.

    Syntax::

        do(line,
           ...)

    where each ``line`` is one of::

        let(name=body)   # Haskell:  name <- expr (see below on expr)

        body             # Haskell:  expr

    where ``name`` is a Python identifier.

      - Use ``let(name=body)`` when you want to bind a name to the extracted value,
        for use on any following lines. (I.e. when you would use ``>>``.)

      - Use only ``body`` when you just want to sequence operations.
        (I.e. when you would use ``.then(...)``.)

    Above ``body`` is one of:

      - An expression ``expr`` that evaluates to a monad instance.
        (Convenience shorthand for simple values which don't need
         the environment.)

      - A one-argument function which takes in the environment,
        such as ``lambda e: expr``. (Use this if your ``expr``
        needs to access the ``let`` bindings in the environment.)

    If your ``expr`` itself is callable, use the latter format (wrap it as
    ``lambda e: expr``) even if it doesn't need the environment, to prevent
    any misunderstandings in the do-notation processor. (This is only needed,
    if the monad instance which ``expr`` evaluates to, defines __call__.)

    Example::

        do
          a <- [3, 10, 6]
          b <- [100, 200]
          return a + b

    pythonifies as::

        do(let(a=List(3, 10, 6)),      # e.a <- ...
           let(b=List(100, 200)),      # e.b <- ...
           lambda e: List(e.a + e.b))  # access the env via lambda e: ...

    and has the same effect as::

        List(3, 10, 6) >> (lambda a:
        List(100, 200) >> (lambda b:
        List(a + b)))

    A more complex example, pythagorean triples::

        def r(low, high):
            return List.from_iterable(range(low, high))
        pt = do(let(z=r(1, 21)),
                let(x=lambda e: r(1, e.z+1)),  # needs the env to access "z"
                let(y=lambda e: r(e.x, e.z+1)),
                lambda e: List.guard(e.x*e.x + e.y*e.y == e.z*e.z),
                lambda e: List((e.x, e.y, e.z)))

    has the same effect as::

        def r(low, high):
            return List.from_iterable(range(low, high))
        pt = r(1, 21)  >> (lambda z:
             r(1, z+1) >> (lambda x:
             r(x, z+1) >> (lambda y:
             List.guard(x*x + y*y == z*z).then(
             List((x,y,z))))))

    Note the line with the guard; no ``let``, no new binding on the next line.
    """
    # Notation used by the monad implementation for the bind and sequence
    # operators, with any relevant whitespace.
    bind = " >> "
    seq  = ".then"

    class env:
        def __init__(self):
            self.names = set()
        def assign(self, k, v):
            self.names.add(k)
            setattr(self, k, v)
        # simulate lexical closure property for env attrs
        #   - freevars: set of names that "fall in" from a surrounding lexical scope
        def close_over(self, freevars):
            names_to_clear = {k for k in self.names if k not in freevars}
            for k in names_to_clear:
                delattr(self, k)
            self.names = freevars.copy()

    # stuff used inside the eval
    e = env()
    def begin(*exprs):  # args eagerly evaluated by Python
        # begin(e1, e2, ..., en):
        #   perform side effects e1, e2, ..., e[n-1], return the value of en.
        return exprs[-1]

    allcode = ""
    names = set()  # names seen so far (working line by line, so textually!)
    bodys = []
    begin_is_open = False
    for j, item in enumerate(lines):
        is_first = (j == 0)
        is_last  = (j == len(lines) - 1)

        if isinstance(item, (tuple, list)):
            name, body = item
        else:
            name, body = None, item
        if name and not name.isidentifier():
            raise ValueError("name must be valid identifier, got '{}'".format(name))
        bodys.append(body)

        freevars = names.copy()  # names from the surrounding scopes
        if name:
            names.add(name)

        # TODO: check also arity (see unpythonic.arity.arity_includes)
        if callable(body):  # takes in the environment?
            code = "bodys[{j:d}](e)".format(j=j)
        else:  # doesn't need the environment
            code = "bodys[{j:d}]".format(j=j)

        if begin_is_open:
            code += ")"
            begin_is_open = False

        # monadic-bind or sequence to the next line, leaving only the appropriate
        # names defined in the env (so that we get proper lexical scoping
        # even though we use an imperative stateful object to implement it)
        if not is_last:
            if name:
                code += "{bind:s}(lambda {n:s}:\nbegin(e.close_over({fvs}), e.assign('{n:s}', {n:s}), ".format(bind=bind, n=name, fvs=freevars)
                begin_is_open = True
            else:
                if is_first:
                    code += "{bind:s}(lambda _:\nbegin(e.close_over(set()), ".format(bind=bind)
                    begin_is_open = True
                else:
                    code += "{seq:s}(\n".format(seq=seq)

        allcode += code
    allcode += ")" * (len(lines) - 1)

#    print(allcode)  # DEBUG

    # The eval'd code doesn't close over the current lexical scope,
    # so provide the necessary names as its globals.
    return eval(allcode, {"e": e, "bodys": bodys, "begin": begin})


##################################
# Some monads
##################################

# Identity monad (cf. identity function) - no-op, just regular function composition.
#
# Shows the structure in its simplest form.
#
class Identity:
    def __init__(self, x):    # unit: x: a  -> M a
        self.x = x
    def __rshift__(self, f):  # bind: x: (M a), f: (a -> M b)  -> (M b)
                              # (Here "x" means self.x; OO(F)P implementation.)
        # bind ma f = join (fmap f ma)
        return self.fmap(f).join()
        # manual implementation of bind
#        return f(self.x)
    def __str__(self):
        clsname = self.__class__.__name__
        return "<{} {}>".format(clsname, self.x)
    # Lift a regular function into an Identity monad producing one.
    @classmethod
    def lift(cls, f):         # lift: f: (a -> b)  -> (a -> M b)
        return lambda x: cls(f(x))
    # http://learnyouahaskell.com/functors-applicative-functors-and-monoids
    def fmap(self, f):        # fmap: x: (M a), f: (a -> b)  -> (M b)
        cls = self.__class__
        return cls(f(self.x))
    def join(self):           # join: x: M (M a)  -> M a
        cls = self.__class__
        if not isinstance(self.x, cls):
            raise TypeError("Expected a nested {} monad, got {} with data {}".format(cls, type(self.x), self.x))
        return self.x

# The following two monads, Maybe and List, are essentially containers.
#
# This article may help:
#   https://wiki.haskell.org/Monads_as_containers

# Maybe - simple error handling.
#
# When computing with Maybes, a value of Maybe(Empty) is taken to indicate that
# an error occurred, and that the rest of the computation is to be skipped.
#
# The magic is that the calling code needs no if/elses checking for an
# error return value - those are refactored into this monad.
#
# To take the Haskell analogy further, we could use MacroPy and case classes
# to approximate an ADT (algebraic data type) that actually consists of
# data constructors Just and Nothing.
#
# Here, for simplicity of implementation:
#   - Nothing is represented as Maybe(Empty), and
#   - Just x is represented as Maybe(x).
#
# "Maybe" is essentially a sketch of how to implement an exception system
# in pure FP. It is not really needed in Python, since exceptions are already
# available for error handling that skips the rest of the computation.
# But it is a simple, yet informative, example of a monad.
#
class Maybe:
    def __init__(self, x):    # unit: x: a -> M a
        self.x = x

    def __rshift__(self, f):  # bind: x: (M a), f: (a -> M b)  -> (M b)
        # bind ma f = join (fmap f ma)
        return self.fmap(f).join()
        # manual implementation of bind
#        if self.x is Empty:
#            return self
#        else:
#            return f(self.x)     # this f already returns monadic output

    # Sequence a.k.a. "then"; standard notation ">>" in Haskell.
    #
    # Given a Maybe monad, bind into a function that ignores its argument
    # and returns that Maybe monad.
    #
    # Can be used for sequencing tasks when the data value is not important.
    # Especially useful with guard().
    #
    # For an explanation, see State.then().
    #
    def then(self, f):  # self: M a,  f : M b  -> M b
        cls = self.__class__
        if not isinstance(f, cls):
            raise TypeError("Expected a monad of type {}, got {} with data {}".format(cls, type(f), f))
        return self >> (lambda _: f)

    # Introducing the guard function:
    #
    # https://en.wikibooks.org/wiki/Haskell/Alternative_and_MonadPlus#guard
    #
    @classmethod
    def guard(cls, b):  # bool -> Maybe  (for the Maybe monad)
        if b:
            return cls(True)  # Maybe with data in it; doesn't matter what it is,
                              # the value is not intended to be actually used.
        else:
            return cls(Empty) # Nothing - binding this to a function
                              # short-circuits the computation!

    def __str__(self):
        if self.x is Empty:
            return "<Nothing>"
        else:
            return "<Just {}>".format(self.x)

    # Lift a regular function into a Maybe-producing one.
    # This is essentially compose(unit, f).
    @classmethod
    def lift(cls, f):         # lift: f: (a -> b)  -> (a -> M b)
        return lambda x: cls(f(x))

    # Roughly, a functor (in the Haskell sense) is a container one can
    # "map" over; monads are a subset of functors.
    # http://learnyouahaskell.com/functors-applicative-functors-and-monoids
    def fmap(self, f):        # fmap: x: (M a), f: (a -> b)  -> (M b)
        if self.x is Empty:
            return self
        else:
            cls = self.__class__
            return cls(f(self.x))

    def join(self):           # join: x: M (M a)  -> M a
        cls = self.__class__
        if not isinstance(self.x, cls) and self.x is not Empty:
            raise TypeError("Expected a nested {} monad, got {} with data {}".format(cls, type(self.x), self.x))
        # a maybe of a maybe - unwrap one layer
        if self.x is Empty:
            return self
        else:
            return self.x

# List - multivalued functions.
#
# This is especially useful, also in Python. Usage examples further below.
#
class List:
    def __init__(self, *elts):  # unit: x: a -> M a
        # For convenience with liftm2: accept Empty as a special *item* that,
        # when passed to the List constructor, produces an empty list.
        #
        # The issue is that the standard liftm2 takes a regular function,
        # where the output is just one item; the construction of the
        # List container for this item occurs inside liftm2. Hence,
        # the special meaning "no result" must be encoded somehow,
        # if we want to be able to create also empty lists from
        # liftm2'd functions.
        #
        # This is why we don't use Python's None; placing a single None
        # into a List is a valid use case. The only way to make the signaling
        # almost out-of-band is to have a magic value that cannot be confused
        # with anything else.
        #   https://en.wikipedia.org/wiki/In-band_signaling#Other_applications
        #
        if len(elts) == 1 and elts[0] is Empty:
            self.x = ()
        else:
            self.x = elts

    def __rshift__(self, f):  # bind: x: (M a), f: (a -> M b)  -> (M b)
        # bind ma f = join (fmap f ma)
        return self.fmap(f).join()
        # done manually, essentially List.from_iterable(flatmap(lambda elt: f(elt), self.x))
        #return List.from_iterable(result for elt in self.x for result in f(elt))

    # Sequence a.k.a. "then"; standard notation ">>" in Haskell.
    #
    # Given a List monad, bind into a function that ignores its argument
    # and returns that List monad.
    #
    # Can be used for sequencing tasks when the data value is not important.
    # Especially useful with guard().
    #
    # For an explanation, see State.then().
    #
    def then(self, f):  # self: M a,  f : M b  -> M b
        cls = self.__class__
        if not isinstance(f, cls):
            raise TypeError("Expected a monad of type {}, got {} with data {}".format(cls, type(f), f))
        return self >> (lambda _: f)

    @classmethod
    def guard(cls, b):  # bool -> List   (for the list monad)
        if b:
            return cls(True)  # List with one element; doesn't matter what it is,
                              # the value is not intended to be actually used.
        else:
            return cls()  # 0-element List - binding this to a function
                          # short-circuits this branch of the computation!

    def __getitem__(self, i): # make List iterable so that "for result in f(elt)" works
        return self.x[i]      # (when f outputs a List monad)

    def __add__(self, other): # concatenation of Lists, for convenience
        cls = self.__class__
        return cls.from_iterable(self.x + other.x)

    def __str__(self):
        clsname = self.__class__.__name__
        return "<{} {}>".format(clsname, self.x)

    @classmethod
    def from_iterable(cls, iterable):  # convenience
        try:
            return cls(*iterable)
        except TypeError: # maybe a generator; try forcing it before giving up.
            return cls(*tuple(iterable))

    def copy(self):
        cls = self.__class__
        return cls(*self.x)

    # Lift a regular function into a List-producing one.
    @classmethod
    def lift(cls, f):         # lift: f: (a -> b)  -> (a -> M b)
        return lambda x: cls(f(x))

    def fmap(self, f):        # fmap: x: (M a), f: (a -> b)  -> (M b)
        cls = self.__class__
        return cls.from_iterable(f(elt) for elt in self.x)

    def join(self):           # join: x: M (M a)  -> M a
        cls = self.__class__
        if not all(isinstance(elt, cls) for elt in self.x):
            raise TypeError("Expected a nested {} monad, got {}".format(cls, self.x))
        # list of lists - concat them
        return cls.from_iterable(elt for sublist in self.x for elt in sublist)

# Writer - debug logging, pure FP way.
#
# This is still container-ish.
#
class Writer:
    def __init__(self, x, log=""):  # unit: x: a -> M a
        self.data = (x, log)

    def __rshift__(self, f):        # bind: x: (M a), f: (a -> M b)  -> (M b)
        # works but causes extra verbosity in log, since fmap also logs itself.
#        return self.fmap(f).join()
        # so let's do this one manually.
        x0, log = self.data
        x1, msg = f(x0).data
        cls     = self.__class__
        return cls(x1, log + msg)

    def __str__(self):
        clsname = self.__class__.__name__
        return "<{} {}>".format(clsname, self.data)

    # Lift a regular function into a debuggable one.
    # http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html
    @classmethod
    def lift(cls, f):               # lift: f: (a -> b)  -> (a -> M b)
        return lambda x: cls(f(x), "[{} was called on {}]".format(f, x))

    def fmap(self, f):              # fmap: x: (M a), f: (a -> b)  -> (M b)
        x0, log = self.data
        x1      = f(x0)
        msg     = "[fmap was called with {} on {}]".format(f, x0)
        cls     = self.__class__
        return cls(x1, log + msg)

    def join(self):                 # join: x: M (M a)  -> M a
        cls = self.__class__
        if not isinstance(self.data, cls):
            raise TypeError("Expected a nested {} monad, got {} with data {}".format(cls, type(self.data), self.data))
        (x, inner_log), outer_log = self.data
        return cls(x, outer_log + inner_log)

# State - actually, a state processor.
#
# Warning: advanced material. Mind-bending parts inside.
#
# In Python, in the same vein as unfold(), we don't really need the State monad,
# at least for its basic uses - we have generators for implicit handling of state
# (although they use genuine destructive imperative updates, whereas this doesn't).
#
# But let's take a look at what this thing is, anyway, because in doing so,
# we will see a different way of thinking about monads.
#
#
# Main sources:
#
#   http://brandon.si/code/the-state-monad-a-tutorial-for-the-confused/
#   https://wiki.haskell.org/Monads_as_computation
#   https://en.wikibooks.org/wiki/Haskell/Understanding_monads/State
#   https://wiki.haskell.org/State_Monad
#
# Notes:
#
# - The main idea here is *monads as computation*. It's still kinda-a container,
#   but what we wrap here is not just a data value, but instead a computation
#   (a function).
#
# - Usage consists of two alternating phases:
#
#    1) State processor s -> (a, s). Old state in; a data value and new state out.
#    2) The code at the use site - do something with "a", then tell phase 1
#       which state processor to run next.
#
# - The state s only becomes bound when the chain starts running - and we start
#   the chain only after we're done composing it. In the call to run, we give
#   the chain the initial state it will start in - then the monad does the
#   plumbing required to pass the state across the state processor calls,
#   in a functional (FP) manner. Just like in an FP loop, there is no mutation,
#   but in effect, the state changes (via fresh instances).
#
#   Until the chain runs, everything is, so to speak, just hypothetical -
#   planning what we'll do once we get our hands on an initial state value.
#   This is an important difference from the data container monads, above.
#
class State:
    # In this monad, construction of instances and unit() (monadic "return")
    # are different.
    #
    # The constructor just wraps a state processor function into a State object.
    #
    def __init__(self, f):  # State constructor: f: s -> (a, s)
        if not callable(f):
            raise TypeError("Expected a callable s -> (a, s), got {}".format(f))
        self.processor = f

    # Take a value "a"; make a function that takes a state value "s",
    # and returns (a, s).
    #
    @classmethod
    def unit(cls, a):              # unit: a -> M a  i.e.  a -> State(s -> (a, s))
        # Obviously, the state processor that always returns "a"
        # must completely ignore "s", so the definition is:
        return cls(lambda s: (a, s))

    # Accessor: run the wrapped function, starting from given state s.
    #
    # Haskell calls this runState, and there it is technically only a getter
    # with a weird name; but Haskell's automatic currying allows using it
    # as both a getter for the wrapped function as well as a command to run it.
    #
    # In Python, it's like saying self.processor (just get the function)
    # vs. self.processor(s) (run it with argument s). So to mimic Haskell,
    # we could have called the data attribute "run" instead of "processor",
    # but that's just confusing.
    #
    def run(self, s):
        return self.processor(s)

    # Run and return just the data value.
    def eval(self, s):
        a, sprime = self.run(s)
        return a

    # Run and return just the state value.
    def exec(self, s):
        a, sprime = self.run(s)
        return sprime

    # Bind: composition of state processors. This is the tricky bit.
    #
    #
    # Here f is expected to be  a -> State(s -> (a, s))
    # i.e. take a *data value* (not state value!),
    # return a state processor.
    #
    # Now, what is this crazy kind of function that takes a *data value*
    # and turns that into *a state processor*? Well, somewhat similarly to a
    # "lambda as a code block" in Lisp, it's not really a function (although
    # just like there, formally it is!): it is the code block we bind into!
    # It's something to be performed *between* two processings of the state.
    #
    # It makes perfect sense that that code block should take a data value
    # (the data value part of the result of the current state processor),
    # do something with that (maybe save or display it), and then tell us
    # what to do next - i.e. provide a new state processor for us.
    #
    #
    # Secondly: how can this work correctly with three or more chainees?
    # (This is perhaps one of the most difficult points to grasp at first.)
    #
    # At first glance, it would seem the state processor in the middle runs
    # twice: once as the second operation of the first State instance, and
    # again as the first operation of the second State instance. But actually,
    # that's wrong.
    #
    # Remember that binding is essentially function composition, and we return
    # the composed function. Hence, in a chain A >> B >> C (ignoring the data
    # values for now), A >> B becomes a new composed state processor - let's
    # name it D - and the chain is transformed into D >> C. At this point,
    # *nothing has actually run yet*, we are just planning what to do
    # by building composed functions. Now the second bind composes a new
    # state processor out of D and C. Obviously, to run all the given operations,
    # we must eventually run both D and C. Here running D internally runs both
    # A and B, so each of A, B and C will run exactly once - as they should.
    #
    #
    # Finally, note that (in Haskell) the type of the state value stays
    # the same in a chain, whereas the type of the data value may change.
    # Python doesn't enforce that, but people familiar with this idea
    # will likely expect it.
    #
    def __rshift__(self, f):        # bind: x: (M a), f: (a -> M b)  -> (M b)
                                    # i.e.  x: s -> (a, s), f: a -> State(s -> (b, s))  -> State(s -> (b, s))
                                    # where x means self.processor.
        def composed(s):  # s -> (a, s)
            # See also the comments on "wrap" and "unwrap" at
            # https://en.wikibooks.org/wiki/Haskell/Understanding_monads/State

            a, sprime = self.run(s)           # apply current processor

            # Take "the contained data value from inside the monad" - which,
            # in our case, is *the data result of our wrapped computation* -
            # and send that to the code block we bind into.
            #
            # The code block then gives us a new State monad, which wraps
            # the next state processor to run.
            #
            # The beauty is that the code block *doesn't even see* the
            # state value - it only gets the data value of the result,
            # just as if computing with functions which need no state.
            #
            # The monad is "shunting" the state value around the code that's
            # only interested in the data, and delivering the state to only
            # where it's actually needed - into the actual state processors!
            #
            new_processor = f(a)

            return new_processor.run(sprime)  # then apply new processor
        return State(composed)

    # Sequence a.k.a. "then"; standard notation ">>" in Haskell.
    #
    # Make a composition that runs the currently wrapped computation
    # (s -> (a, s)), throws away the data value result "a";
    # then runs the given computation f, and returns its result.
    #
    # This is useful for just advancing the state, when the returned
    # data value is not important (e.g. an intermediate value before
    # the one that we'll eventually want to extract).
    #
    # Usage:
    #
    #   doProc1.then(doProc2)...
    #
    # where doProc1 and doProc2 are State objects.
    #
    def then(self, f):  # self: State(s -> (a, s)),  f: State(s -> (b, s))  -> State(s -> (b, s))
        cls = self.__class__
        if not isinstance(f, cls):
            raise TypeError("Expected a monad of type {}, got {} with data {}".format(cls, type(f), f))

        # Definition taken from
        #   https://wiki.haskell.org/Monads_as_computation
        #
        # Why does this definition work?
        #  - f is a State monad
        #  - We bind to a function (the lambda here) that ignores its argument
        #    and returns that State monad as the computation to perform next.
        #
        return self >> (lambda _: f)

    def __str__(self):
        clsname = self.__class__.__name__
        return "<{} {}>".format(clsname, self.processor)

    # return the state value being passed around
    # (usage: bind or sequence into this; don't call directly!)
    @classmethod
    def get(cls):  # no input -> State(s -> (s, s))
        return cls(lambda s: (s, s))

    # replace the current state value with s
    @classmethod
    def put(cls, s):  # s -> State(s -> (Empty, s))
        return cls(lambda _: (Empty, s))  # no value for "a"

    # https://wiki.haskell.org/State_Monad
    @classmethod
    def modify(cls, f):  # f: (s -> s)  -> State(s -> (Empty, s))
        return cls.get() >> (lambda s: cls.put(f(s)))

    @classmethod
    def gets(cls, f):  # f: (s -> a)  -> State(s -> (a, s))
        return cls.get() >> (lambda s: cls.unit(f(s)))

    @classmethod
    def lift(cls, f):               # lift: f: (a -> b) -> (a -> M b)
                                    # i.e.  f: (a -> b) -> (a -> State(s -> (b, s)))
        raise NotImplementedError() # TODO later? Does this operation make sense?

    def fmap(self, f):              # fmap: x: (M a), f: (a -> b)  -> (M b)
                                    # i.e.  x: State(s -> (a, s)), f: (a -> b)  -> State(s -> (b, s))
        # Definition taken from
        #   https://en.wikibooks.org/wiki/Haskell/Understanding_monads/State
        return (liftm(State, f))(self)

    def join(self):                 # join: x: M (M a)  -> M a
                                    # i.e.  x: State(s -> (State(s -> (a, s)), s))  -> State(s -> (a, s))
        raise NotImplementedError() # TODO later? Due to dependency on s', we must make a function
                                    # that can run later (once the state value becomes available),
                                    # not run anything immediately.
                                    # See here for a definition: https://wiki.haskell.org/Monads_as_containers

# Reader: a read-only shared environment.
#
# More mind-bending parts inside.
#
# Something between a container and a computation.
#
# On the other hand, it's really just a function, from a particular environment
# of type e, and it provides a monad API.
#
# Based on:
#   https://wiki.haskell.org/Monads_as_containers
#   https://www.mjoldfield.com/atelier/2014/08/monads-reader.html
#   https://blog.ssanj.net/posts/2014-09-23-A-Simple-Reader-Monad-Example.html
#   https://stackoverflow.com/questions/14178889/what-is-the-purpose-of-the-reader-monad
#
class Reader:
    def __init__(self, f):    # constructor: f: (e -> a)  -> Reader e a
        if not callable(f):   # Note! Essentially, Reader e a = (e -> a), with a wrapper.
            raise TypeError("Expected a callable e -> a, got {}".format(f))
        self.r = f

    @classmethod
    def unit(cls, x):         # unit: a -> Reader e a
        return cls(lambda _: x)  # similar to State.unit() - ignore the parameter, return the given data value.

    # Similarly to State, the environment only becomes bound when we
    # run() the Reader; until then, it's all just planning.
    def run(self, env):       # e -> a
        return self.r(env)

    # Get the environment.
    # (Usage: Reader.ask() >> (lambda env: ...))
    @classmethod
    def ask(cls):   # -> Reader a a
        return cls(lambda env: env)

    # Run the environment through the given function f,
    # and monadically return the result.
    # https://www.mjoldfield.com/atelier/2014/08/monads-reader.html
    @classmethod
    def asks(cls, f):  # f: (e -> a)  -> Reader e a
        return cls.ask() >> (lambda env: cls.unit(f(env)))

    # Run a computation in a modified environment.
    def local(self, f):       # f: (e -> e), r: Reader e a  -> Reader e a
        cls = self.__class__
        return cls(lambda env: self.run(f(env)))

    def fmap(self, f):        # fmap: f: (a -> b), r: Reader e a  -> Reader e b
        cls = self.__class__
        return cls(lambda env: f(self.run(env)))

    def join(self):           # join: (Reader e (Reader e a))  -> Reader e a
        cls = self.__class__
        return cls(lambda env: (self.run(env)).run(env))

    # From https://wiki.haskell.org/Monads_as_containers
    #
    # bind is taking a computation which may read from the environment
    # before producing a value of type "a", and a function from values
    # of type "a" to computations which may read from the environment
    # before returning a value of type "b", and composing these together,
    # to get a computation which might read from the (shared) environment,
    # before returning a value of type "b".
    #
    def __rshift__(self, f):  # bind: r: (Reader e a), f: (a -> Reader e b)  -> Reader e b
        return self.fmap(f).join()

    def then(self, f):  # TODO: is this useful here?
        cls = self.__class__
        if not isinstance(f, cls):
            raise TypeError("Expected a monad of type {}, got {} with data {}".format(cls, type(f), f))
        return self >> (lambda _: f)


##################################
# Some monad-enabled functions
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
    # This is the syntax - first, construct a monadic value, then send it
    # to a chain of operations using bind (here denoted ">>").
    #
    print(Identity(4) >> id_sqrt >> id_sqrt)

    ########################################################################
    # Maybe: compose functions that may raise an error
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

    ########################################################################
    # Abstracting the previous solution further: let's use "liftm2".

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
        return Mx.fmap(lambda a: (a,) + My.x)  # we must .x to get the tuple inside.
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


    ########################################################################
    # Another use for List - nondetermistic evaluation.

    # This approach works also for turning random searches into
    # nondeterministic systematic ones (at the expense of lots of
    # CPU time - hence, place any filters as early as you can!).

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

    # More efficient - don't form redundant combinations.
    # https://en.wikibooks.org/wiki/Haskell/Alternative_and_MonadPlus#guard
    #
    def r(low, high):
        return List.from_iterable(range(low, high))
    pt = r(1, 21)  >> (lambda z:  # hypotenuse; upper bound for the length of the other sides
         r(1, z+1) >> (lambda x:  # one of the other sides will be the shorter one
         r(x, z+1) >> (lambda y:
         List((x,y,z)) if x*x + y*y == z*z else List())))
    print(pt)

    # Using guard() to perform the checking:
    #
    pt = r(1, 21)  >> (lambda z:
         r(1, z+1) >> (lambda x:
         r(x, z+1) >> (lambda y:
         List.guard(x*x + y*y == z*z) >> (lambda _:  # The dummy is the dummy data element from the guard.
                                                     # If the guard fails, this part doesn't even run,
                                                     # because the dummy variable here is bound, in turn,
                                                     # *to each element produced by the guard*.
         List((x,y,z))))))
    print(pt)

    # Since guard() is only used for control flow (the dummy data value from
    # inside the List monad it returns is ignored), we can use then()
    # instead of bind:
    #   M1.then(M2)  is the same as  M1 >> (lambda _: M2)
    # whence the above can be rewritten as:
    #
    pt = r(1, 21)  >> (lambda z:
         r(1, z+1) >> (lambda x:
         r(x, z+1) >> (lambda y:
         List.guard(x*x + y*y == z*z).then(
         List((x,y,z))))))
    print(pt)

    # This is quite similar in spirit to the Racket solution; List.guard()
    # plays the role of the nondeterministic "assert".
    # https://github.com/Technologicat/python-3-scicomp-intro/blob/master/examples/beyond_python/choice.rkt

    # This would also be idiomatic Haskell, but Python's syntax doesn't do this
    # solution justice; it really needs the "do notation" to look readable.
    #
    # Haskell is the natural habitat for that, so it has it out of the box.
    #   https://wiki.haskell.org/Monads_as_computation#Do_notation
    #   https://en.wikibooks.org/wiki/Haskell/do_notation
    #
    # For Racket, there's a monad library which adds that:
    #   https://github.com/tonyg/racket-monad
    #   http://eighty-twenty.org/2015/01/25/monads-in-dynamically-typed-languages
    #
    # Python's syntax simply can't be easily customized to accommodate this.
    #
    # But see:
    #   https://github.com/JadenGeller/Guac   (for PyPy3)
    #   https://pypi.org/project/hymn/   which runs on Hy:
    #   https://github.com/hylang/hy     which is a Lisp built on top of Python.

    ########################################################################
    # Customizing List - computing with discrete probability densities.
    #
    # What is the probability distribution of rolling two six-sided dice?

    # pairs (x, p); one die
    dN_pdf = lambda n: List(*range(1, n+1)).fmap(lambda x: (x, 1/n))

    d6_pdf = dN_pdf(6)  # let's make it six-sided

    def probsum(xp1, xp2):  # combination rule for two pairs;  (a, a) -> a
        x1,p1 = xp1
        x2,p2 = xp2
        return (x1 + x2, p1*p2)

    # apply monadically
    mprobsum = liftm2(List, probsum)  # (M a, M a) -> M a
    twod6_pdf = mprobsum(d6_pdf, d6_pdf)

    # combine items for the same x... manually!
    final = {}
    for x,p in twod6_pdf:
        if x not in final:
            final[x] = p
        else:
            final[x] += p
    print(sorted(((x, p) for x,p in final.items())))

    # Actually, the algorithm for combining matching results belongs in join(),
    # so let's put it there:
    #
    class DiscretePDF(List):  # a DiscretePDF is a List...
        def join(self):       # ...with a customized join().
            # Note that the algorithm is imperative, but the interface is FP.
            # We mutate only the local variables of this function.
            final = {}
            for sublist in self.x:
                for x,p in sublist:
                    if x not in final:
                        final[x] = p
                    else:
                        final[x] += p
            return self.from_iterable(sorted(((x, p) for x,p in final.items())))

    # Now:
    dN_pdf = lambda n: DiscretePDF(*range(1, n+1)).fmap(lambda x: (x, 1/n))
    d6_pdf = dN_pdf(6)  # six-sided
    mprobsum = liftm2(DiscretePDF, probsum)  # (M a, M a) -> M a
    twod6_pdf = mprobsum(d6_pdf, d6_pdf)
    print(twod6_pdf)

    # Extending this to the case of three dice is now just:
    threed6_pdf = mprobsum(twod6_pdf, d6_pdf)
    print(threed6_pdf)

    ########################################################################
    # State processor

    # Example inspired by:
    #
    # http://brandon.si/code/the-state-monad-a-tutorial-for-the-confused/
    # https://wiki.haskell.org/State_Monad

    def processor(s):  # s -> (a, s);   s: int, a: str
        values = ["a", "b", "c", "d", "e"]
        return (values[s%5], s+1)  # note: data choice based on the *old* state (in this example)
    getNext = State(processor)

    # Invoke the wrapped processor by run(initial_state).
    #
    # It returns a tuple (value, new_state).
    #
    print(getNext.run(0))

    # Wrapped processors can be composed with bind:
    #
    inc3 = getNext >> (lambda x:
           getNext >> (lambda y:
           getNext >> (lambda z:
               State.unit(z))))  # unit a.k.a. monadic "return"

    # ...and then run:
    #
    print(inc3.run(0))

    # DANGER: unit() returns the specified result, with the *current* state,
    # (which is not necessarily the state corresponding to that result):
    #
    inc3 = getNext >> (lambda x:
           getNext >> (lambda y:
           getNext >> (lambda z:
               State.unit(y))))  # return an earlier data value, with *current* state
    print(inc3.run(0))

    # If you only want to advance the state without looking at the data,
    # use then() instead of bind:
    #
    inc3DiscardedValues = getNext.then(getNext).then(getNext)
    print(inc3DiscardedValues.run(0))   # return final value and new state

    # Using put() to replace the current state:
    #
    tmp = getNext.then(getNext).then(getNext).then(State.put(42)).then(getNext)
    print(tmp.run(0))

    tmp = (State.put(42)).then(getNext)  # same effect, since put() "overwrites" the state
    print(tmp.run(0))

    # Using get() to get the current state.
    #
    # Don't call it directly as a method of the monad instance;
    # that does nothing useful (it only sees the initial state).
    #
    # Instead, insert it into the chain by binding or sequencing,
    # just like any other operation:
    #
    tmp2 = getNext.then(getNext) >> (lambda s: State.get())
    tmp2 = getNext.then(getNext) >> (lambda _: State.get())  # s unused; same
    tmp2 = getNext.then(getNext).then(State.get())           # same (by def of then())
    print(tmp2.run(0))

    # Other helpers: modify, gets.

    # modify() replaces the current state like put(), but takes a function,
    # that takes the current state as input and returns the new desired state:
    #
    tmp3 = getNext.then(getNext).then(State.modify(lambda s: 2 * s)).then(getNext)
    print(tmp3.run(0))

    # gets() retrieves the current state, feeds that into the given function,
    # and then unit()s (monadic "return"s) the function's return value
    # as the new data value, leaving the state unchanged.
    #
    tmp4 = getNext.then(getNext).then(State.gets(lambda s: "the state is now {}".format(s)))
    print(tmp4.run(42))

    ########################################################################
    # Using the State monad to compute Fibonacci numbers.

    # Borrowing this from the example in unfold.py.
    #
    # The monad allows us to move the countdown outside,
    # separating the actual state processor.
    #
    # (Generators also allow us to do that; recall fibo3.py.)
    #
    def fibo(state):  # s -> (a, s)
        a,b = state
        return (a, (b, a+b))  # data value, new state

    def fibos(howmany):
        # Choose operation type here (in this example, it's fibo).
        op = State(fibo)

        # Next, let's define the code we bind into.
        #
        # Remember: do something with "a" (the data result), then return
        # the next state processor to be applied.
        #
        # Note that this function doesn't care about - and indeed doesn't
        # even have access to - the state value s.
        #
        lst = []  # this will gather the results...
        def save_and_continue(a):  #  a -> State(s -> (a, s))
            lst.append(a)  # ...because closures and lexical scoping.
            return op  # next time, just do the same thing again.

        # Set up the first operation.
        processor = op

        # Build the chain: one "op", and as many "save_and_continue"s as we want.
        for count in range(howmany):
            processor = (processor >> save_and_continue)

        # Start the chained processor from the desired initial state.
        processor.run((1, 1))

        return lst

    print(fibos(20))

    # Another way.
    #
    # This solution uses the shunting capabilities of the State monad
    # without using the chaining (much).
    #
    def fibos2(howmany):
        def do_nothing(state):
            # ...doing nothing here...
            return (Empty, state)  # ...and leaving the state unchanged.
        NoOp = State(do_nothing)  # wrap it

        lst = []
        def save(a):  #  a -> State(s -> (a, s))
            lst.append(a)
            return NoOp  # "do nothing next"; avoid advancing the state twice...

        # ...because now each iteration of the loop will first run State(fibo),
        # which already advances the state.
        #
        # Instead of NoOp, we could use any operation that does not change the state.
        # We do need a second operation, because bind is defined to run our
        # function (i.e. save()) *between two operations*.
        #
        processor = (State(fibo) >> save)

        # exec returns just the new state, so in the loop, we are telling the
        # State monad to start from the current state, compute the new state
        # (while saving the data result because of the bind to save()),
        # and return the new state.
        #
        # The loop here gets only "s" and doesn't even see "a",
        # whereas save() gets only "a" and doesn't even see "s".
        #
        s = (1, 1)
        for count in range(howmany):
            s = processor.exec(s)

        return lst

    ########################################################################
    # Reader monad

    # A read-only shared environment.

    # Simple examples, thanks to:
    #   https://www.mjoldfield.com/atelier/2014/08/monads-reader.html

    # The Reader returned by ask() just retrieves the environment.
    r = Reader.ask()
    print(r.run("hello"))  # here we use just a string as the environment, but it could be anything.

    # local() runs a computation in a modified environment:
    r2 = r.local(lambda env: "{} sauce".format(env))
    print(r2.run("Chocolate"))

    # We can restore the original environment by ask()ing again:
    r3 = r2.then(Reader.ask())
    #r3 = r2 >> (lambda _: Reader.ask())  # equivalent
    print(r3.run("Chocolate"))

    # The environment is passed implicitly, using the monad pattern.
    #
    # Cf. other strategies for this, e.g. lexical closures, global variables.
    #
    # Lambda has been called "the ultimate dependency injection framework"...
    #   http://eed3si9n.com/herding-cats/Reader.html
    #
    # (Among other, more classical "ultimates": http://library.readscheme.org/page1.html )
    #
    def f(x):
        # (Note that the return value of f() is a Reader monad;
        #  it still needs to be run() with an environment
        #  to get an actual result.)
        return Reader.ask() >> (lambda env:
               Reader.unit((x, env)))
    print(f(10).run("hi there"))

    # asks() creates a Reader that evaluates the given function (e -> a),
    # and monadically returns the result.
    #
    r4 = Reader.asks(len)
    print(r4.run("banana"))

    # Simple example of composing functions that use Reader, thanks to:
    #   https://blog.ssanj.net/posts/2014-09-23-A-Simple-Reader-Monad-Example.html

    tom = Reader.ask() >> (lambda env:
          Reader.unit("{} This is Tom.".format(env)))  # return the output using unit() (monadic "return")

    jerry = Reader.ask() >> (lambda env:
            Reader.unit("{} This is Jerry.".format(env)))

    tomAndJerry = tom >> (lambda t:    # t is the return value of tom
                  jerry >> (lambda j:  # j is the return value of jerry
                  Reader.unit("{}\n{}".format(t, j))))

    # The string given as argument to run() becomes the environment.
    print(tomAndJerry.run("Who is this?"))

    # Above, the environment was just a string, but this being Python,
    # it's obviously duck-typed.
    #
    # Let's demonstrate with a dict. We could use the bunch from let.py
    # (instead of dict) to get a more natural-looking syntax for the lookups.
    #
    r1 = Reader.ask() >> (lambda env:
         Reader.unit("Hi, I'm r1, env.foo is {}".format(env["foo"])))
    r2 = Reader.ask() >> (lambda env:
         Reader.unit("Hi, I'm r2, env.bar is {}".format(env["bar"])))
    r1andr2 = r1 >> (lambda val1:
              r2 >> (lambda val2:
              Reader.unit("{}\n{}".format(val1, val2))))
    print(r1andr2.run({'foo': 1, 'bar': 2}))


def test_do_notation():
#    List(3, 10, 6) >> (lambda a:
#    List(100, 200) >> (lambda b:
#    List(a + b))))
    print(do(let(a=List(3, 10, 6)),   # e.a <- ...
             let(b=List(100, 200)),   # e.b <- ...
             lambda e: List(e.a + e.b)))  # output, not named

    def r(low, high):
        return List.from_iterable(range(low, high))
#    pt = r(1, 21)  >> (lambda z:
#         r(1, z+1) >> (lambda x:
#         r(x, z+1) >> (lambda y:
#         List.guard(x*x + y*y == z*z).then(
#         List((x,y,z))))))
#    print(pt)
    pt = do(let(z=r(1, 21)),
            let(x=lambda e: r(1, e.z+1)),
            let(y=lambda e: r(e.x, e.z+1)),
            lambda e: List.guard(e.x*e.x + e.y*e.y == e.z*e.z),  # no name, no capture
            lambda e: List((e.x, e.y, e.z)))
    print(pt)

    # silly, but need to test it works even if the first body assigns no name
    print(do(List("repeat", "twice"),  # because this List has two elements
             let(a=List(3, 10, 6)),
             let(b=List(100, 200)),
             lambda e: List(e.a + e.b)))

if __name__ == '__main__':
    main()
    test_do_notation()
