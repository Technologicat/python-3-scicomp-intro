# -*- coding: utf-8 -*-
#
# This is a definition file, only seen at the C level when a Cython module
# performs a "cimport mysum".

cdef double sum(double[::1] a) nogil
