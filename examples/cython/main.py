#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main script for testing.

Created on Wed Mar 28 15:00:47 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np

# Cython modules can be imported just like any Python module
import ddot
import dgemm
import nocopy

def test_ddot():
    print("ddot")
    print("Successful usage")
    a = np.random.random((10,))
    b = np.random.random((10,))
    # call like any Python function, provided that the datatypes match!
    c = ddot.ddot(a, b)
    assert np.allclose(c, np.dot(a,b))  # NumPy's dot should do the same thing

    print(a, b, c)

    print("Error cases")
    try:
        c = ddot.ddot([1,2,3], [4,5,6])  # wrong container type (list)
    except TypeError as e:
        print(e)
    try:
        a = np.arange(10, dtype=int)
        b = a.copy()
        x = ddot.ddot(a, b)  # wrong element datatype
    except ValueError as e:
        print(e)

def test_dgemm():
    print("dgemm")
    print("Successful usage")
    A = np.random.random((5,5))
    B = np.random.random((5,5))
    C = dgemm.dgemm(A, B)
    assert np.allclose(C, np.dot(A,B))

def test_nocopy():
    # Run the nocopy example
    print("Nocopy example")
    nocopy.test()

def main():
    test_ddot()
    test_dgemm()
    test_nocopy()

if __name__ == '__main__':
    main()
