# -*- coding: utf-8 -*-
#
# Set Cython compiler directives. This section must appear before any code!
#     http://docs.cython.org/en/latest/src/reference/compilation.html
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Extension type (cdef class) example.

A Python-level wrapper for a generic C pointer (void pointer, void *).

Created on Thu Mar 29 18:31:35 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

cdef class PointerWrapper:
    cdef set(self, void * p):
        self.data = p
