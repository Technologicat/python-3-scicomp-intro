#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Computing prime numbers in Python.

Meant as a demonstration of generators; not necessarily efficient.

Created on Mon Feb 12 15:55:53 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

from itertools import takewhile, islice
import simpletimer

# https://swizec.com/blog/python-and-lazy-evaluation/swizec/5148

def naturals(start=0):
    i = start
    while True:
        yield i
        i += 1

# naive algorithm
# time-inefficient, memory-efficient: no internal storage
def primes():
    yield 2
    for f in naturals(start=1):
        n = 2*f + 1
        if not any(p != n and n % p == 0 for p in takewhile(lambda x: x*x <= n, primes())):
            yield n

# naive algorithm
# time-efficient, memory-inefficient: keep a list of already generated primes
def memoprimes():
    memo = []
    def gen():
        memo.append(2)
        yield 2
        for f in naturals(start=1):
            n = 2*f + 1
            if not any(p != n and n % p == 0 for p in takewhile(lambda x: x*x <= n, memo)):
                memo.append(n)
                yield n
    return gen()

# Sieve of Eratosthenes, using infinite streams.
#
# Will crash in Python for n ⪆ 2500 because the maximum recursion depth
# will be exceeded, but shows the idea.
#
def sieve():
    def remove_multiples_of(m, iterable):
        for k in iter(iterable):
            if k % m != 0:
                yield k
    stream = naturals(start=2)
    while True:  # invariant: the first element of stream is prime
        m = next(stream)
        yield m
        stream = remove_multiples_of(m, stream)

def take(n, iterable):
    return tuple(islice(iter(iterable), n))

def main():
    print(take(10, primes()))
    print(take(10, memoprimes()))
    print(take(10, sieve()))

    n = 2500
    print("Performance for first {:d} primes:".format(n))
    if n <= 5000:
        with simpletimer.SimpleTimer("naive 1: "):
            take(n, primes())
    with simpletimer.SimpleTimer("naive 2: "):
        take(n, memoprimes())
    if n <= 2500:
        with simpletimer.SimpleTimer("sieve: "):
            take(n, sieve())

if __name__ == '__main__':
    main()
