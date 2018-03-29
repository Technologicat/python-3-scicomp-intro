# -*- coding: utf-8 -*-
#
# Set Cython compiler directives. This section must appear before any code!
#     http://docs.cython.org/en/latest/src/reference/compilation.html
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Example of separate definition and implementation files, to export at C level.

Main script.

Created on Wed Mar 28 15:18:45 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np
cimport mysum  # import at the C level

def test():
    a = np.arange(10, dtype=np.float64)
    print(mysum.sum(a))  # use just like any Python function (as long as the datatypes match)
