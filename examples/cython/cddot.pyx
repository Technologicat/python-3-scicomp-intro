# -*- coding: utf-8 -*-
#
# Set Cython compiler directives. This section must appear before any code!
#     http://docs.cython.org/en/latest/src/reference/compilation.html
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Cython example - C functions (cdef functions).

Created on Wed Mar 28 15:36:38 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np

# - cdef makes a C function, visible only at the C level.
#   - By default, visible only in this module.
#   - To export a C level function, make a definition file (lecture 8, slides 12-13).
# - nogil at the end of the signature means this C function can be called
#   *also without the GIL*. (It doesn't release the GIL.)
#
cdef double cddot(double [::1] a, double [::1] b) nogil:
    cdef unsigned int k
    cdef unsigned int n = a.shape[0]
    cdef double out = 0.0

    for k in range(n):
        out += a[k] * b[k]

    return out

def test():
    a = np.random.random((10,))
    b = np.random.random((10,))
    c = cddot(a, b)   # ...but it's fine to call cddot() even when we have the GIL.
    assert np.allclose(c, np.dot(a,b))
    print(a, b, c)
