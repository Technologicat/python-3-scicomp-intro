#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Using the List monad as an amb operator for Python. See also monads.py."""

class Empty:
    def __repr__(self):
        return "<Empty>"
Empty = Empty()  # sentinel

#   liftm:   f: (a -> r)       ->  lifted: (M a -> M r)
#   liftm2:  f: ((a, b) -> r)     ->  lifted: ((M a, M b) -> M r)
#
# In this module, ">>" means monadic bind.

def liftm(M, f):
    def lifted(Mx):
        if not isinstance(Mx, M):
            raise TypeError("argument: expected monad {}, got {} with data {}".format(M, type(Mx), Mx))
        return Mx >> (lambda x: M(f(x)))
    return lifted

def liftm2(M, f): # M: monad type,  f: ((a, b) -> r)  ->  lifted: ((M a, M b) -> M r)
    def lifted(Mx, My):
        if not isinstance(Mx, M):
            raise TypeError("first argument: expected monad {}, got {} with data {}".format(M, type(Mx), Mx))
        if not isinstance(My, M):
            raise TypeError("second argument: expected monad {}, got {} with data {}".format(M, type(My), My))
        return Mx >> (lambda x: My >> (lambda y: M(f(x, y))))
    return lifted

class List:
    def __init__(self, *elts):  # unit: x: a -> M a
        # For convenience with liftm2: accept the sentinel Empty as a special
        # *item* that, when passed to the List constructor, produces an empty list.
        #
        # The standard liftm2 takes a regular function, where the output is
        # just one item; the construction of the List container for this item
        # occurs inside liftm2. Hence, the special meaning "no result" must be
        # encoded somehow, if we want to be able to create also empty lists from
        # liftm2'd functions.
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
    def then(self, f):  # self: M a,  f : M b  -> M b
        cls = self.__class__
        if not isinstance(f, cls):
            raise TypeError("Expected a monad of type {}, got {} with data {}".format(cls, type(f), f))
        return self >> (lambda _: f)

    @classmethod
    def guard(cls, b):  # bool -> List   (for the list monad)
        if b:
            return cls(True)  # List with one element; value not intended to be actually used.
        else:
            return cls()  # 0-element List; short-circuit this branch of the computation.

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

def main():
    """Nondetermistic evaluation using the List monad."""

    # Essentially, we just make a cartesian product:
    print(List(3, 10, 6) >> (lambda a:  # semantically, lists of possible choices
          List(100, 200) >> (lambda b:
          List(a + b))))

    # ...but this becomes interesting when we add a filter:
    is_even = lambda x: List(x) if x % 2 == 0 else List()
    print(List(4, 5)   >> (lambda a:
          List(11, 14) >> (lambda b:
          List(a + b)))
          >> is_even)

    # Classic amb problem: find pythagorean triples
    def r(low, high):
        return List.from_iterable(range(low, high))
    pt = r(1, 21) >> (lambda a:
         r(1, 21) >> (lambda b:
         r(1, 21) >> (lambda c:
         List((a,b,c)) if a*a + b*b == c*c else List())))
    # accept only sorted entries
    pts = pt >> (lambda t: List(t) if t[0] < t[1] < t[2] else List())
    print(pts)

    # More efficient - don't form redundant combinations.
    # https://en.wikibooks.org/wiki/Haskell/Alternative_and_MonadPlus#guard
    pt = r(1, 21)  >> (lambda z:  # hypotenuse; upper bound for the length of the other sides
         r(1, z+1) >> (lambda x:  # one of the other sides will be the shorter one
         r(x, z+1) >> (lambda y:
         List((x,y,z)) if x*x + y*y == z*z else List())))
    print(pt)

    # Use guard() to perform the checking:
    pt = r(1, 21)  >> (lambda z:
         r(1, z+1) >> (lambda x:
         r(x, z+1) >> (lambda y:
         List.guard(x*x + y*y == z*z) >> (lambda _:  # The dummy comes from the guard. If the
                                                     # guard fails, this lambda doesn't even run.
         List((x,y,z))))))
    print(pt)

    # Since the data value from guard() is not needed,
    # we can use then() instead of bind. Final code:
    pt = r(1, 21)  >> (lambda z:
         r(1, z+1) >> (lambda x:
         r(x, z+1) >> (lambda y:
         List.guard(x*x + y*y == z*z).then(
         List((x,y,z))))))
    print(pt)

if __name__ == '__main__':
    main()
