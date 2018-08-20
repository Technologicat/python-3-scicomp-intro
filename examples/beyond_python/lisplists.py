#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demonstration of Lisp-like linked lists in Python.

Created on Sun Jul 29 12:22:40 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

from functools import wraps, reduce as foldl

# https://github.com/Technologicat/unpythonic
from unpythonic import call, trampolined, jump, SELF

def foldr(function, sequence, initial=None):
    """Right fold."""
    return foldl(function, reversed(sequence), initial)

def compose(*functions):
    """Compose an iterable of one-argument functions."""
    def compose2(f, g):
        return lambda x: f(g(x))
    return foldl(compose2, functions, lambda x: x)  # op(acc, elt)

def flip(function):
    """Decorator. Reverse positional arguments of function."""
    @wraps(function)
    def flipped(*args, **kwargs):
        return function(*reversed(args), **kwargs)
    return flipped

# @call a class to make a singleton instance.
# The sentinel could be any object, but we prefer one with a nice repr.
@call
class nil:
    def tolist(self):  # for completeness, since cons cells have it
        return []
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
        # special lispy printing for linked lists
        @trampolined  # <-- enable stack space optimized tail calls
        def llist_repr(cell, acc):
            newacc = lambda: acc + [repr(cell.car)]  # delay evaluation with lambda
            if cell.cdr is nil:
                return newacc()
            elif isinstance(cell.cdr, cons):
                return jump(SELF, cell.cdr, newacc())  # optimized tail call
            else:
                return False  # not a linked list
        result = llist_repr(self, []) or [repr(self.car), ".", repr(self.cdr)]
        return "({})".format(" ".join(result))

def car(x):
    if not isinstance(x, cons):
        raise TypeError("Expected a cons, got {} with value {}".format(type(x), x))
    return x.car
def cdr(x):
    if not isinstance(x, cons):
        raise TypeError("Expected a cons, got {} with value {}".format(type(x), x))
    return x.cdr
caar = compose(car, car)
cadr = compose(car, cdr)  # "car of the cdr"
cdar = compose(cdr, car)
cddr = compose(cdr, cdr)
# Racket defines these up to caaaar, ..., cddddr.

def llist(*elts):
    """Create a linked list.

    Parameters:
        elts: sequence
            See help(reversed) for the description and limitations.

    Returns:
        cons instance
            The first cons cell in the list.
    """
    @trampolined
    def conschain(seq, acc):
        if not seq:
            return acc
        x, *xs = seq
        return jump(SELF, xs, cons(x, acc))
    return conschain(reversed(elts), nil)

# Alternatively, we may express llist as a foldr with cons.
# (John Hughes, 1984: Why Functional Programming Matters.)
#
# Python's reduce expects op(acc, elt), so we must reverse
# the positional arguments of cons.
#
snoc = flip(cons)
def llist2(*elts):
    """Create a linked list.

    Same as llist(); just a different implementation.
    """
    return foldr(snoc, elts, nil)

# A foldl with cons reverses a linked list.
def reverse(ll):
    """Reverse a linked list."""
    return foldl(snoc, ll, nil)

# A foldr with cons also appends linked lists.
#
def append(ll1, ll2):
    """Append two linked lists."""
    # .tolist() because https://docs.python.org/3/library/functions.html#reversed
    return foldr(snoc, ll1.tolist(), ll2)

def appendn(*lls):  # appendn(ll, ...)
    """Append one or more linked lists.

    (Appending one list does nothing.)

    Parameters:
        lls: iterable
            The linked lists. Will be appended from left to right:
            appendn(a, b, c) == llist(*a, *b, *c)

    Returns:
        cons instance
            The first cons cell in the new list.
    """
    acc, *rest = lls
    for ll in rest:
        acc = append(acc, ll)
    return acc

def appendn_fp(*lls):  # same, implemented using an FP loop.
    """Append one or more linked lists.

    Same as append(); just a different implementation.
    """
    @trampolined
    def appendloop(acc, seq):
        if not seq:
            return acc
        ll, *lls = seq
        return jump(SELF, append(acc, ll), lls)
    acc, *rest = lls
    return appendloop(acc, rest)

@trampolined
def member(x, ll):
    """Walk linked list and check if item x is in it.

    Returns:
        The matching cons cell if x was found; False if not.
    """
    if not isinstance(ll, cons):
        raise TypeError("Expected a cons, got {} with value {}".format(type(x), x))
    if not isinstance(ll.cdr, cons) and ll.cdr is not nil:
        raise ValueError("This cons is not a linked list; current cell {}".format(ll))
    if ll.car == x:      # match
        return ll
    elif ll.cdr is nil:  # last cell, no match
        return False
    else:
        return jump(SELF, x, ll.cdr)

def lzip(*lls):
    """Zip linked lists, producing a tuple of linked lists.

    Built-in zip() works too, but produces tuples.
    """
    return tuple(map(llist, *lls))  # tuple() to force the generator

def main():
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
    print([f(t) for f in [caar, cdar, cadr, cddr]])

    q = llist(cons(1, 2), cons(3, 4))  # list of pairs, not a tree!
    print(q)
    print([f(q) for f in [caar, cdar, cadr, cddr]])

    l = llist(1, 2, 3)
    print([f(l) for f in [car, cadr, cdr, cddr]])
    print(member(2, l))
    print(member(5, l))

    # tuple unpacking syntax
    c = cons(1, 2)
    l, r = c
    print("unpacking a pair", l, r)

    ll = llist(1, 2, 3)
    a, b, c = ll
    print("unpacking a list", a, b, c)

    print("tolist()", ll.tolist())

    print(llist2(1, 2, 3))

    print(reverse(ll))

    print(append(llist(1, 2, 3), llist(4, 5, 6)))
    print(appendn(llist(1, 2, 3), llist(4, 5, 6), llist(7, 8, 9)))
    print(appendn_fp(llist(1, 2, 3), llist(4, 5, 6), llist(7, 8, 9)))
    print(tuple(zip(llist(1, 2, 3), llist(4, 5, 6))))
    print(lzip(llist(1, 2, 3), llist(4, 5, 6)))

if __name__ == '__main__':
    main()
