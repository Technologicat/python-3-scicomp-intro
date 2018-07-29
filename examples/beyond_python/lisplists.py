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

    class cons:  # cons cell a.k.a. pair. Immutable, like in Racket.
        def __init__(self, v1, v2):
            self.car = v1
            self.cdr = v2
            self._immutable = True
        def __setattr__(self, k, v):
            if hasattr(self, "_immutable"):
                raise AttributeError("Assignment to immutable cons cell not allowed")
            super().__setattr__(k, v)
        # https://stackoverflow.com/questions/40242526/how-to-overload-argument-unpacking-operator
        #     c = cons(1, 2)
        #     l, r = c
        # or for linked list:
        #     ll = llist(1, 2, 3)
        #     head, tail = ll
        def __getitem__(self, i):
            if i == 0: return self.car
            if i == 1: return self.cdr
            raise IndexError()
        def tolist(self):  # assuming we are a linked list.
            out = []
            o = self
            while True:
                if not isinstance(o.cdr, cons) and o.cdr is not nil:
                    raise ValueError("This cons is not a linked list")
                out.append(o.car)
                if o.cdr is nil:
                    break
                o = o.cdr
            return out
        def __repr__(self):
#            return "({} . {})".format(repr(self.car), repr(self.cdr))  # DEBUG
            @trampolined
            def doit(obj, acc):
                if obj.cdr is nil:  # last cons cell in a Lisp list
                    return acc + [repr(obj.car)]
                elif isinstance(obj.cdr, cons):  # Lisp list continues
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

    def llist(*elts):  # make Lisp list, like Racket's (list) function
        @trampolined
        def conschain(xs, acc):
            if not xs:
                return acc
            x, *rest = xs
            return jump(SELF, rest, cons(x, acc))
        return conschain(reversed(elts), nil)

    @trampolined
    def member(x, ll):
        if not isinstance(ll.cdr, cons) and ll.cdr is not nil:
            raise ValueError("This cons is not a linked list")
        if ll.car == x:
            return ll
        if ll.cdr is nil:  # last cell, didn't match
            return False
        return jump(SELF, x, cdr(ll))

    try:
        c = cons(1, 2)
        c.car = 3  # immutable, should fail
    except AttributeError:
        pass
    else:
        assert False

    print(cons(1, 2))  # pair
    print(cons(1, cons(2, cons(3, nil))))  # list
    print(llist(1, 2, 3))
    print(cons(cons(cons(nil, 3), 2), 1))  # improper list
    print(llist(1, 2, cons(3, 4), 5, 6))

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
    head, tail = ll
    print("head", head, "tail", tail)

    # llist can be expressed as a foldr with cons.
    # (See Hughes, 1984: Why Functional Programming Matters.)
    #
    # Python's reduce expects f(acc, elt), so we must reverse
    # the positional arguments of cons.
    #
    # First let's define some utilities.
    from functools import wraps, reduce as foldl
    def flip(f):
        @wraps(f)
        def flipped(*args, **kwargs):
            return f(*reversed(args), **kwargs)
        return flipped
    def foldr(function, sequence, initial=None):
        return foldl(function, reversed(sequence), initial)

    snoc = flip(cons)
    def llist2(*elts):
        return foldr(snoc, elts, nil)

    print(llist2(1, 2, 3))

    # A foldl with cons reverses a list.
    def reverse(ll):
        return foldl(snoc, ll.tolist(), nil)
    print(reverse(ll))

if __name__ == '__main__':
    main()
