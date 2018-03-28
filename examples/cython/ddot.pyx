"""Simple Cython example.

Vector-vector dot product, double precision.

Created on Wed Mar 28 14:57:38 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

def ddot(double [::1] a, double [::1] b):
    """def ddot(double [::1] a, double [::1] b):

Vector-vector dot product, double precision.
"""
    cdef unsigned int k
    cdef unsigned int n = a.shape[0]    # memoryviews have a .shape, just like NumPy arrays
    cdef double out = 0.0

    for k in range(n):       # Becomes a C loop when compiled. Cython knows the datatypes
        out += a[k] * b[k]   # and memory layouts, and no Python objects are used here.

    return out
