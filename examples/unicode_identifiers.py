#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# In Python 3, identifiers can be Unicode.
#
# Roughly speaking, "alphabetical" characters are OK in variable names and similar.
#
# This is mainly just something to know, as it's not that commonly used - but
# if you really insist on writing math like this, you may be interested in
# installing a "LaTeX input method" for your OS.

import math

α = 90  # degrees
π = math.pi
ℵ = float("inf")
あ = "A"  # With Unicode, we'll never run out of symbol names.

# But:
# ∞ = float("inf")  # invalid, not in the right character class for an identifier

# These can be used just like any variable:
#
print("α in radians: %g" % (α * 2*π/360))
print("ℵ has the value %g" % ℵ)
print("あ is pronounced as %s" % あ)