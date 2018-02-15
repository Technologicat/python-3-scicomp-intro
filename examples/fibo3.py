#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fibonacci numbers, using a generator.

Adapted to Python 3, from the answer by alex at:

https://stackoverflow.com/questions/3323001/what-is-the-maximum-recursion-depth-in-python-and-how-to-increase-it

Created on Wed Feb 14 03:08:19 2018

@author: jje
"""

from itertools import islice

def fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def takeone(iterable, n):
    return tuple(islice(iterable, n, n+1))[0]

def main():
    for num in islice(fib(), 1000):
        print(num)

    print("The 10000th Fibonacci number is")
    print(takeone(fib(), 10000))

if __name__ == '__main__':
    main()
