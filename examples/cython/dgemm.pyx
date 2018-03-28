# -*- coding: utf-8 -*-
#
# Set Cython compiler directives. This section must appear before any code!
#     http://docs.cython.org/en/latest/src/reference/compilation.html
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Cython example: releasing the GIL.

Matrix-matrix multiply, double precision.

Created on Wed Mar 28 15:09:44 2018

@author: jje
"""

import numpy as np    # just a usual Python import

def dgemm(double [:,::1] A, double [:,::1] B):
    cdef unsigned int i, j, k
    cdef unsigned int n = A.shape[0]
    cdef unsigned int m = B.shape[1]  # the datatype double [:,::1] ensures ndim=2.
    cdef unsigned int p = A.shape[1]
    cdef double [:,::1] out = np.zeros((n,m), dtype=np.float64, order='C')  # or empty(), ones(), ...

    if B.shape[0] != p:
        raise ValueError('Incompatible input shapes ({:d},[:d}), ({:d},{:d})'.format(n,p,B.shape[0],m))

    with nogil:
        for i in range(n):
            for j in range(m):
                for k in range(p):
                    out[i,j] += A[i,k] * B[k,j]

    return np.asanyarray(out)  # return np.array, not memoryview (with no extra copying of data)
