#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SymPy and the derivation of Hermite interpolation polynomials.

Created on Fri Dec  1 04:15:10 2017

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import sympy as sy

def hermite(k):  # Derive C**k continuous Hermite interpolation polynomials for the interval [0, 1]
    order = 2*k + 1
    *A,x = sy.symbols('a0:%d,x' % (order+1))

    w   = sum(a*x**i for i,a in enumerate(A))  # as a symbolic expression
    λw  = lambda x0: w.subs({x: x0})  # as a Python function; subs: symbolic substitution
    wp  = [sy.diff(w, x, i) for i in range(1,1+k)]  # diff: symbolic differentiation
    λwp = [(lambda expr: lambda x0: expr.subs({x: x0}))(expr) for expr in wp]  # why two lambdas: lecture notes sec. 5.8

    zero,one = sy.S.Zero, sy.S.One
    w0,w1 = sy.symbols('w0, w1')
    eqs  = [λw(zero) - w0, λw(one)  - w1]  # eqs. in form LHS = 0; see sy.solve()
    dofs = [w0, w1]

    for i,f in enumerate(λwp):
        d0_name = 'w%s0' % ((i+1) * 'p')  # p = 'prime', to denote differentiation
        d1_name = 'w%s1' % ((i+1) * 'p')
        d0,d1 = sy.symbols('%s, %s' % (d0_name, d1_name))
        eqs.extend([f(zero) - d0, f(one)  - d1])
        dofs.extend([d0, d1])

    coeffs = sy.solve(eqs, A)
    solution = sy.collect(sy.expand(w.subs(coeffs)), dofs)

    N = [solution.coeff(dof) for dof in dofs]  # result

    return tuple(zip(dofs, N))  # pairs (dof, interpolating function)

def main():
    for j in range(3):
        print(hermite(j))

if __name__ == '__main__':
    main()

