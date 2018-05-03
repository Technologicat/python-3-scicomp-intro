#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""3D plotting in  Matplotlib.

Created on Fri Dec  1 04:13:19 2017

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as axes3d

tt = np.linspace(0, 4*np.pi, 1001)
xx = np.cos(tt)
yy = np.sin(tt)
zz = np.linspace(0, 1, len(tt))

fig = plt.figure(1)
fig.patch.set_color((1,1,1))  # fig. background, RGB
fig.patch.set_alpha(1.0)  # fig. background, opacity
left_bot_w_h = [0.02, 0.02, 0.96, 0.96]  # more space to edges
ax = axes3d.Axes3D(fig, rect=left_bot_w_h)
# see also ax.plot_wireframe, ax.plot_surface, ax.plot_trisurf
ax.plot(xx, yy, zz, label='Example spiral')
ax.view_init(34, -130)  # elev, azim
ax.axis('tight')
ax.legend(loc='best')
plt.xlabel(r'$x$')
plt.ylabel(r'$y$')
ax.set_title(r'$z$')  # note! No “zlabel” due to Matplotlib's history as a 2D plotter.
plt.savefig('spiral.svg')

