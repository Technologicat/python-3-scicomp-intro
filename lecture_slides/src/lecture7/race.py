#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 23:42:30 2018

@author: jje
"""

import threading    # standard library
import time
import numpy as np

def f(k):
    global x
    y = x    # read shared state
    time.sleep(1e-6)
    y += k   # compute (this step does not access x)
    x = y    # update shared state

out = []
for i in range(1000):
    global x
    x = 1
    threads = [ (lambda jj: threading.Thread(target=f, args=(jj,)))(j) for j in range(1,21) ]
    for T in threads:
        T.start()
    for T in threads:
        T.join()
    out.append(x)

hist,bin_edges = np.histogram(out)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
print(hist,bin_centers)
print("Most common bin center: {v}".format(v=bin_centers[np.argmax(hist)]))
