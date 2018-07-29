#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demonstration of Lisp-like linked lists in Python.

Created on Sun Jul 29 12:22:40 2018

@author: jje
"""

# https://github.com/Technologicat/unpythonic
from unpythonic import immediate, trampolined, jump, SELF

def main():
    # @immediate a class to make a singleton instance.
    # The sentinel could be any object, but we prefer one with a nice repr.
    @immediate
    class nil:
        def __repr__(self):
            return "nil"

    # Make our linked lists support the iterator protocol, so that they can be
    # used in for loops, tuple unpacking, and such.
    # https://stackoverflow.com/questions/16301253/what-exactly-is-pythons-iterator-protocol
    # https://stackoverflow.com/questions/40242526/how-to-overload-argument-unpacking-operator
    class ConsIterator:
        def __init__(self, startcell):
            if not isinstance(startcell, cons):
                raise TypeError("Expected a cons, got {} with value {}".format(type(startcell), startcell))
            self.lastread = None
            self.cell = startcell

        def __iter__(self):
            return self

        def __next__(self):
            if not self.lastread:
                self.lastread = "car"
                return self.cell.car
            elif self.lastread == "car":
                if isinstance(self.cell.cdr, cons):  # linked list, general case
                    self.cell = self.cell.cdr
                    self.lastread = "car"
                    return self.cell.car
                elif self.cell.cdr is nil:           # linked list, last cell
                    raise StopIteration()
                else:                                # just a pair
                    self.lastread = "cdr"
                    return self.cell.cdr
            elif self.lastread == "cdr":
                raise StopIteration()
            else:
                assert False, "Invalid value for self.lastread '{}'".format(self.lastread)

    # Cons cell a.k.a. pair. Immutable, like in Racket.
    class cons:
        def __init__(self, v1, v2):
            self.car = v1
            self.cdr = v2
            self._immutable = True
        def __setattr__(self, k, v):
            if hasattr(self, "_immutable"):
                raise AttributeError("Assignment to immutable cons cell not allowed")
            super().__setattr__(k, v)
        def __iter__(self):
            return ConsIterator(self)
        def tolist(self):
            return [x for x in self]  # implicitly using __iter__
        def __repr__(self):
#            return "({} . {})".format(repr(self.car), repr(self.cdr))  # DEBUG
            @trampolined
            def doit(obj, acc):
                if obj.cdr is nil:  # last cons cell in a linked list
                    return acc + [repr(obj.car)]
                # we need the second condition to distinguish from trees: cons(cons(1, 2), cons(3, 4))
                # TODO: still doesn't work if the tree contains three levels; check how Racket does it.
                elif isinstance(obj.cdr, cons) and \
                     (isinstance(obj.cdr.cdr, cons) or obj.cdr.cdr is nil):  # linked list continues
                    return jump(doit, obj.cdr, acc + [repr(obj.car)])
                else:
                    return [repr(obj.car), ".", repr(obj.cdr)]
            return "({})".format(" ".join(doit(self, [])))

    def car(x):
        if not isinstance(x, cons):
            raise TypeError("Expected a cons, got {} with value {}".format(type(x), x))
        return x.car
    def cdr(x):
        if not isinstance(x, cons):
            raise TypeError("Expected a cons, got {} with value {}".format(type(x), x))
        return x.cdr
    caar = lambda x: car(car(x))
    cadr = lambda x: car(cdr(x))
    cdar = lambda x: cdr(car(x))
    cddr = lambda x: cdr(cdr(x))

    def llist(*elts):  # Lisp list constructor, like Racket's (list) function
        @trampolined  # <-- enable stack space optimized tail calls
        def conschain(xs, acc):
            if not xs:
                return acc
            x, *rest = xs
            return jump(SELF, rest, cons(x, acc))  # optimized tail call
        return conschain(reversed(elts), nil)

    @trampolined
    def member(x, ll):
        """Walk ll and check if x is in it.

        Return the matching cell if it is; False if not.
        """
        if not isinstance(ll.cdr, cons) and ll.cdr is not nil:
            raise ValueError("This cons is not a linked list")
        if ll.car == x:
            return ll
        elif ll.cdr is nil:  # last cell, didn't match
            return False
        else:
            return jump(SELF, x, cdr(ll))

    try:
        c = cons(1, 2)
        c.car = 3  # immutable cons cell, should fail
    except AttributeError:
        pass
    else:
        assert False

    print(cons(1, 2))  # pair
    print(cons(1, cons(2, cons(3, nil))))  # list
    print(llist(1, 2, 3))
    print(llist(1, 2, cons(3, 4), 5, 6))  # a list may also contain pairs as items
    print(cons(cons(cons(nil, 3), 2), 1))  # improper list

    t = cons(cons(1, 2), cons(3, 4))  # binary tree
    print(t)
    print(caar(t), cdar(t), cadr(t), cddr(t))

    l = llist(1, 2, 3)
    print(car(l))
    print(cadr(l))
    print(cdr(l))
    print(cddr(l))
    print(member(2, l))
    print(member(5, l))

    c = cons(1, 2)
    l, r = c
    print("pair", l, r)

    ll = llist(1, 2, 3)
    a, b, c = ll
    print("list", a, b, c)

    print("with tolist()", ll.tolist())

    # We could also express llist as a foldr with cons.
    # (John Hughes, 1984: Why Functional Programming Matters.)
    #
    # Python's reduce expects op(acc, elt), so we must reverse
    # the positional arguments of cons.
    #
    # First let's define some utilities.
    from functools import wraps, reduce as foldl
    def flip(f):
        """Decorator. Reverse positional arguments of f."""
        @wraps(f)
        def flipped(*args, **kwargs):
            return f(*reversed(args), **kwargs)
        return flipped
    def foldr(function, sequence, initial=None):
        """Right fold."""
        return foldl(function, reversed(sequence), initial)

    snoc = flip(cons)
    def llist2(*elts):
        return foldr(snoc, elts, nil)

    print(llist2(1, 2, 3))

    # A foldl with cons reverses a list.
    def reverse(ll):
        return foldl(snoc, ll, nil)
    print(reverse(ll))

if __name__ == '__main__':
    main()
