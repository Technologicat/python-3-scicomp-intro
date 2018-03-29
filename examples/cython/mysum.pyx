# -*- coding: utf-8 -*-
#
# Set Cython compiler directives. This section must appear before any code!
#     http://docs.cython.org/en/latest/src/reference/compilation.html
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Example of separate definition and implementation files, to export at C level.

Library.

Created on Wed Mar 28 15:18:45 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

cdef double sum(double[::1] a) nogil:
    cdef unsigned int k, n = a.shape[0]
    cdef double out = 0.0
    for k in range(n):
        out += a[k]
    return out
