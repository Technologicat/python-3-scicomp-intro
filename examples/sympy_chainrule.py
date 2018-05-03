#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SymPy, the chain rule, and custom expression manipulation.

Created on Fri Dec  1 04:14:17 2017

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import sympy as sy
from sympy.core.function import UndefinedFunction

def nameof_as_symbol(sym):
    if hasattr(sym, 'name'):
        return sy.symbols(sym.name, **sym.assumptions0)
    else:  # an undefined function is anonymous, but its class has __name__
        return sy.symbols(sym.__class__.__name__, **sym.assumptions0)

def strip(expr):  # for printing: remove (maybe long) argument lists from unknown functions
    if isinstance(expr.__class__, UndefinedFunction):
        return nameof_as_symbol(expr)  # we strip args, no need to recurse into it
    elif expr.is_Atom:
        return expr
    else:  # compound other than an undefined function
        newargs = [strip(x) for x in expr.args]
        cls = type(expr)
        return cls(*newargs)

def main():
    x = sy.symbols('x')

    # Unknown function
    λf,λg = sy.symbols('f,g', cls=sy.Function)

    # Applied function
    g = λg(x)  # “g = g(x)”; the symbol name inside must be unique, so λg is single use only
    f = λf(g)  # f = f(g)

    # With the above definitions, SymPy automatically applies the chain rule:
    D = sy.diff(f, x).doit()
    sy.pprint(strip(D))

main()

