import numpy as np
import matplotlib.pyplot as plt

xx = np.linspace(0, 1, 201)
yy = np.sin(np.pi*xx)

fig1 = plt.figure(1)
fig1.clf()

ax = plt.subplot(1,1, 1)
ax.plot(xx,yy)

plt.axis('tight')
plt.grid(b=True, which='both')
plt.xlabel(r"$x$")
plt.ylabel(r"$y$")
plt.title(r"$\sin(x)$")

plt.show()
