#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Basic usage of Matplotlib.

Created on Fri Dec  1 04:12:08 2017

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np
import matplotlib.pyplot as plt

xx = np.linspace(0, 1, 101)
yy1 = np.sin(np.pi * xx)
yy2 = np.sin(2 * np.pi * xx)

plt.figure(1, figsize=(8,6))  # size optional
plt.clf()  # clear (Spyder does not close)
plt.plot(xx, yy1, label=r'$\sin(\pi x)$')  # internal TeX interpreter
plt.plot(xx, yy2, label=r'$\sin(2 \pi x)$')  # hold enabled by default
plt.xlabel(r'$x$')
plt.ylabel(r'$y$')
plt.title(r'$\sin(\pi x), \sin(2 \pi x)$')  # if you use plt.subplot, see also plt.suptitle
plt.grid(b=True, which='both')
plt.legend(loc='best')
plt.savefig('sin_x.svg')  # or .pdf, .png, etc.

