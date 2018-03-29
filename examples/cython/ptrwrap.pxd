# -*- coding: utf-8 -*-
#
# Definition file for a Python-level wrapper for a generic C pointer (void pointer, void *).
#
cdef class PointerWrapper:
    cdef void * data
    cdef set(self, void * p)
