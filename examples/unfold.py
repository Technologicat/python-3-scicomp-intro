#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Example of an anamorphism (unfold).

https://en.wikipedia.org/wiki/Anamorphism

Created on Tue Apr 17 16:28:28 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

def unfold(proc, state):
    """Unfold (anamorphism); the counterpart of reduce (foldl).

    Parameters:
        proc: function
            Must accept one argument, the current state.
            The state can be any object your particular proc understands.

            Must return either a pair (value, new state),
            or None to signify the end of the generated values.

        state: state
            The initial state, passed to proc to generate
            the first output value.

    Returns:
        List of the generated output values.
    """
    out = []
    while True:
        result = proc(state)
        if result is not None:
            value, state = result
            out.append(value)
        else:
            return out

###########################################
# Examples
###########################################

# x0, x0 + 2, x0 + 4, ...
def step2(state):
    k,countdown = state
    if countdown > 0:
        # pair of (value, new state)
        return (k, (k + 2, countdown - 1))
    # None to signify termination
    return None

def fibo(state):
    a,b,countdown = state
    if countdown > 0:
        return (a, (b, a+b, countdown - 1))

# x0, f(x0), f(f(x0)), ...
def iter(state):
    f,x,countdown = state
    if countdown > 0:
        return (x, (f, f(x), countdown - 1))

# zip(A, B)
def zip_two(state):
    if state is None:
        return None
    (A0,*As),(B0,*Bs) = state
    if len(As) > 0 and len(Bs) > 0:
        return ((A0, B0), (As, Bs))
    else:
        # Last value; we can't terminate yet, because we must return
        # also this value. Signal the next call that we're out of items.
        return ((A0, B0), None)

print(unfold(step2, (10, 5)))
print(unfold(fibo, (1, 1, 20)))
print(unfold(iter, (lambda x: x**2, 2, 6)))
print(unfold(zip_two, ((1, 2, 3, 4), (5, 6, 7))))
