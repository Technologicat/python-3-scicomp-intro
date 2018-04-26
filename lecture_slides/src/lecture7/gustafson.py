#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Illustrate Gustafson's law.

Created on Wed Mar 14 22:59:13 2018

@author: jje
"""

import numpy as np
import matplotlib.pyplot as plt

s = np.linspace(1, 4096, 1001)

fig = plt.figure(1)
plt.clf()
ax = plt.subplot(1,1,1)
out = []
for p in [0.5, 0.75, 0.9, 0.95]:
    S = (1 - p) + s * p
    out.append(S[-1])
    ax.plot(s, S, label=r'$p = {p:g}$'.format(p=p))

ax.set_xlabel(r'$s$')
ax.set_ylabel(r'$S$')
ax.set_xticks([1] + [2**N for N in range(8,13)])
for y in out:
    plt.axhline(y, color='#808080', linestyle='dashed', linewidth=0.5)
    plt.text(1, y, str(y))
plt.legend(loc='best')

plt.savefig('gustafson_plot.svg')
