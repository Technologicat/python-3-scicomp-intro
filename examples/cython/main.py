#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main script for testing.

Created on Wed Mar 28 15:00:47 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np

import ddot  # import just like any Python module

def main():
    print("Successful usage:")
    a = np.random.random((10,))
    b = np.random.random((10,))
    # call like any Python function, provided that the datatypes match!
    x = ddot.ddot(a, b)
    print(a, b, x)

    print("Error cases:")
    try:
        x = ddot.ddot([1,2,3], [4,5,6])  # list objects, wrong container type
    except TypeError as e:
        print(e)
    try:
        c = np.arange(10, dtype=int)
        d = c.copy()
        x = ddot.ddot(c, d)  # wrong element datatype
    except ValueError as e:
        print(e)

if __name__ == '__main__':
    main()
