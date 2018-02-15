#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Computing prime numbers in Python using the Sieve of Eratosthenes.

Meant as a demonstration of generators; not necessarily the most efficient
implementation in Python.

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

# time-inefficient, memory-efficient: no internal storage
def primes():
    yield 2
    for f in naturals(start=1):
        n = 2*f + 1
        if not any(p != n and n % p == 0 for p in takewhile(lambda x: x*x <= n, primes())):
            yield n

# time-efficient, memory-inefficient: keep a list of already generated primes
def memo_primes():
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

# This implementation following SICP 2nd ed. sec. 3.5.1 will crash in Python
# for n ⪆ 2500, because the maximum recursion depth will be exceeded, but it
# shows the idea. (For the recursion depth, see sys.getrecursionlimit().)
#
# In the Scheme programming language, this approach works, because Scheme
# requires tail call elimination, so during runtime there will be no actual
# nested function applications. (Python doesn't!)
#
def sicp_primes():
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
    print(take(10, memo_primes()))
    print(take(10, sicp_primes()))

    n = 2500
    print("Performance for first {:d} primes:".format(n))
    if n <= 5000:
        with simpletimer.SimpleTimer("simple: "):
            take(n, primes())
    with simpletimer.SimpleTimer("memoized: "):
        take(n, memo_primes())
    if n <= 2500:
        with simpletimer.SimpleTimer("SICP: "):
            take(n, sicp_primes())

if __name__ == '__main__':
    main()
