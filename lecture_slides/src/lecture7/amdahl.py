#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Illustrate Amdahl's law.

Created on Wed Mar 14 22:59:13 2018

@author: jje
"""

import numpy as np
import matplotlib.pyplot as plt

s = 2**np.linspace(0, 12, 1001)

fig = plt.figure(1)
plt.clf()
ax = plt.subplot(1,1,1)
for p in [0.5, 0.75, 0.9, 0.95]:
    S = 1 / ((1 - p) + p/s)
    ax.plot(s, S, label=r'$p = {p:g}$'.format(p=p))

ax.set_xscale('log', basex=2)  # https://stackoverflow.com/questions/8887544/making-square-axes-plot-with-log2-scales-in-matplotlib
ax.set_xlabel(r'$s$')
ax.set_ylabel(r'$S$')
ax.set_xticks(2**np.linspace(0,12,13))
ax.set_yticks(np.linspace(2,20,10))
plt.axhline(2, color='#808080', linestyle='dashed', linewidth=0.5)
plt.axhline(4, color='#808080', linestyle='dashed', linewidth=0.5)
plt.axhline(10, color='#808080', linestyle='dashed', linewidth=0.5)
plt.axhline(20, color='#808080', linestyle='dashed', linewidth=0.5)
plt.legend(loc='best')

plt.savefig('amdahl_plot.svg')
