#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A Python-level wrapper for a generic C pointer (void pointer, void *).

Test script. (Slightly extended from the version on the slides.)

Created on Thu Mar 29 18:33:28 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np

from ptrwrap cimport PointerWrapper

def test():
    cdef double [:,::1] A = np.zeros((3,5), dtype=np.float64, order='C')
    A[0,0] = 42.0

    cdef PointerWrapper pw = PointerWrapper()
    pw.set(&A[0,0])

    # When casting a pointer to a memoryview, we must specify the size,
    # as a C pointer doesn't know it!
    #
    # Cython uses the slice syntax to specify the size.
    #
    cdef double [:,::1] B = <double [:3,:5:1]>pw.data
    print(B)

    # Pass pw into a Python-level function - a PointerWrapper is just a Python object.
    example(pw)

# How to pass a C pointer to a Python-level function in a Cython module.
    #
def example(obj):  # ← obj is a generic Python object.
    # obj.data does not exist, since it's not in __dict__.
    # To access the C fields of a cdef class, cast the object to the correct type.
    cdef PointerWrapper pw = <PointerWrapper>obj
    cdef double* p = <double*>pw.data  # we happen to know this pw points to an array of doubles.
    print("{:x}".format(<unsigned long long>pw.data))  # memory address
    print("The first data element has value {:g}".format(p[0]))
