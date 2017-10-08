#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import numpy as np
import matplotlib.pyplot as plt

# compute Fibonacci numbers (accelerated using memoization)
class Fibo:
    memo = {}

    def __init__(self):
        pass

    def __call__(self, k):
        if k in self.memo:
            return self.memo[k]

        k = int(k)
        if k < 0:
            raise ValueError("out of domain; k must be >= 0, got %d" % (k))

        out = None
        if k < 2:
            out = k
        else:
            out = self(k-1) + self(k-2)
        self.memo[k] = out

        return out

def main():
    f = Fibo()
    numbers = [ f(j) for j in range(1000) ]
    print(numbers)

    minf = float("-inf")
    L = [ (math.log10(n) if n > 0 else minf) for n in numbers ]
    print(L)

    print( np.diff(L) )

    plt.figure(1)
    plt.clf()
    plt.plot(L)
    plt.xlabel(r"$n$")
    plt.ylabel(r"$\log_{10}( \mathrm{fib}(n) )$")
    plt.title("Fibonacci numbers (logarithmic scale)")

if __name__ == '__main__':
    main()
    plt.show()