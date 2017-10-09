#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Primitive types.
#
# Note that these are *Python's* primitive types. The number types here
# don't see much use in a NumPy context.

import numbers  # for testing whether integer, real, complex...


# int
#
# no size limit:
#   https://stackoverflow.com/questions/13795758/what-is-sys-maxint-in-python-3
#   (Answer: there isn't.)
#
a = 2**1000
print(type(a))
print(a)
print(isinstance(a, numbers.Integral))  # True, a is an integer
print(isinstance(a, numbers.Real))      # True, a is also real


# str (can contain Unicode)
#
# Technically speaking, the Unicode sandwich has implications here, too:
#
# - With this source file encoded in utf-8, when stored on disk, this is
#   actually an utf-8 encoded bytestream.
#
# - When Python parses the source code upon loading, it decodes the utf-8
#   bytestream into a Unicode string, which is what your program actually sees.
#
# - From the programmer's viewpoint this works transparently; it seems as if
#   "you can type Unicode" into the source file.
#
s = "qwertyüiöp, α β γ, ∂u/∂x"
print(type(s))

# float
#
b    = 1.25
print(isinstance(b, numbers.Real))      # True, b is real
print(isinstance(b, numbers.Rational))  # False, b is a float (general real)
                                        # (but see below, at the end)

c1   = 5/4   # /  is true division (will produce float even if arguments int)
c2   = 5//4  # // is integer division
print(c1)  # 1.25
print(c2)  # 1

# Some useful special values for float:
#
inf  = float('+inf')  # This works in comparisons; x < inf for any finite x.
                      # Compares correctly also if x is int.
minf = float('-inf')
nan  = float('nan')

# complex
#
z1 = 1 + 2j
z2 = 1 + 0j  # the presence of a j component, even with zero value, makes z2 complex.
print(z1)
print(z2)
print(type(z1))
print(type(z2))
print(isinstance(z1, numbers.Complex))  # True, z1 is complex

# bytes (arbitrary binary data)
#
# Remember the Unicode sandwich. Strings can be *encoded* into bytes:
#
b  = s.encode(encoding='utf-8')
print(type(b))

# Bytes (where the bytestream represents encoded text data) can be
# *decoded* into strings.
#
# We could save b into a binary file and read it back later.
# By decoding it, we get back the content of the Unicode string s.
#
s2 = b.decode(encoding='utf-8')
print(type(s2))
print(s2 == s)


##########################################
# NumPy number types

# (These are usually used inside arrays, not on their own.)

import numpy as np

f = np.float64(3.1)
print(type(f))
print(isinstance(f, numbers.Real))  # True

z3 = np.complex128(1+2j)
print(type(z3))
print(isinstance(z3, numbers.Complex))  # True

j = np.int64(5)
print(type(j))
print(isinstance(j, numbers.Integral))  # True


##########################################
# Rationals, base-10 floats

# Not used very often and not built-in types, but it may be useful to be aware
# of these, too.

# If you really want an exact rational number in Python:
#
from fractions import Fraction
r = Fraction(5, 4)
print(r)
print(type(r))
print(isinstance(r, numbers.Rational))  # True, as expected
print(float(r))  # conversion to float

# One can also construct exact fractions out of floats:
#
t = Fraction.from_float(0.25)
print(t)

# Note that because floats are base-2, e.g. 1/10 is not representable exactly:
#
u = Fraction.from_float(0.1)
print(u)  # 3602879701896397/36028797018963968


# If, for some exotic purpose, you really, really want a base-10 float,
# a software implemntation exists in the standard library.
#
# Documentation says:
#     This is an implementation of decimal floating point arithmetic
#     based on the General Decimal Arithmetic Specification:
#
#         http://speleotrove.com/decimal/decarith.html
#
#     and IEEE standard 854-1987:
#
#         http://en.wikipedia.org/wiki/IEEE_854-1987
#
# Decimal floating point has finite precision with arbitrarily large bounds.
#
from decimal import Decimal, getcontext
d1 = Decimal("0.1")
d2 = Decimal(3) / Decimal(10)
print(d1)
print(d2)
print(3*d1 == d2)

getcontext().prec = 18  # set precision (number of mantissa digits)
d3 = Decimal(1) / Decimal(3)
print(d3)
