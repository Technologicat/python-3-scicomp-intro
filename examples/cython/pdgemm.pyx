# -*- coding: utf-8 -*-
#
# Set Cython compiler directives. This section must appear before any code!
#     http://docs.cython.org/en/latest/src/reference/compilation.html
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Cython example: parallelism with OpenMP.

Matrix-matrix multiply, double precision, using a parallel loop.

Created on Thu Mar 29 18:02:06 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np
cimport cython.parallel    # note cimport instead of import (lecture 8, slide 11)

def pdgemm(double [:,::1] A, double [:,::1] B):
    cdef int i, j, k
    cdef int n = A.shape[0]  # indices are signed in OpenMP < 3.0
    cdef int m = B.shape[1]
    cdef int p = A.shape[1]
    cdef double [:,::1] out = np.zeros((n,m), dtype=np.float64, order='C')

    if B.shape[0] != p:
        raise ValueError('Incompatible input shapes ({:d},[:d}), ({:d},{:d})'.format(n,p,B.shape[0],m))

    with nogil:
        for i in cython.parallel.prange(n):      # parallel loop
            for j in range(m):
                for k in range(p):
                    out[i,j] += A[i,k] * B[k,j]  # arrays can be accessed as usual

    return np.asanyarray(out)
