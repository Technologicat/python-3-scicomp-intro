#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Example of an anamorphism (unfold).

https://en.wikipedia.org/wiki/Anamorphism

Created on Tue Apr 17 16:28:28 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

def evens_up_to_10(state):
    if state <= 5:
        # pair of (value, new state)
        return (2*state, state + 1)
    # None to signify termination
    return None

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

print(unfold(evens_up_to_10, 0))
