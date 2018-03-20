#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demonstrate representation and round-off errors in floating point arithmetic.

Created on Tue Mar 20 17:10:46 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import mpmath

mpmath.mp.dps = 1000  # use 1000 decimal places (≈3325 bits)
print(mpmath.mp)

# exact value of float(0.1) - representation error only
r1 = (0.1).as_integer_ratio()
f1 = mpmath.mpf(r1[0]) / r1[1]

# exact value of 3 * float(0.1) - representation error only
three_f1 = 3 * mpmath.mpf(r1[0]) / r1[1]

# float(3 * 0.1) - i.e. floating-point multiply of 3 and 0.1
# both representation error and round-off from the multiplication
r2 = (3 * 0.1).as_integer_ratio()
f2 = mpmath.mpf(r2[0]) / r2[1]

# floating-point sum of three float(0.1) terms
summed_r = (0.1 + 0.1 + 0.1).as_integer_ratio()
summed_f = mpmath.mpf(summed_r[0]) / summed_r[1]

# exact value of float(0.3) - representation error only
r3 = (0.3).as_integer_ratio()
f3 = mpmath.mpf(r3[0]) / r3[1]

print(f1, three_f1, f2, summed_f, f3)
