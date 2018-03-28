# -*- coding: utf-8 -*-
#
# Set Cython compiler directives. This section must appear before any code!
#     http://docs.cython.org/en/latest/src/reference/compilation.html
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Demonstrate that creating a memoryview does not copy the actual data.

Created on Wed Mar 28 15:18:45 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np

def test():
    A = np.random.random((5,5))
    cdef double [:,::1] B = A
    C = np.asanyarray(B)
    print(A is C)                                 # False; A and C are different np.array instances
    print([type(x) for x in (A,B,C)])             # B is a memoryview; A and C are np.arrays

    # https://stackoverflow.com/questions/11264838/how-to-get-the-memory-address-of-a-numpy-array-for-c
    addr_A, readonly_flag_A = A.__array_interface__['data']
    addr_C, readonly_flag_C = C.__array_interface__['data']
    print("{:x}, {:x}, {:x}".format(addr_A, <unsigned long long>&B[0,0], addr_C))
