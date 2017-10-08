#!/usr/bin/env python
# -*- coding: utf-8 -*-

# compute Fibonacci numbers
def f(k):
    k = int(k)
    if k < 0:
        raise ValueError("out of domain")
    if k < 2:
        return k
    else:
        return f(k-1) + f(k-2)

def main():
    numbers = [ f(j) for j in range(30) ]
    print(numbers)

if __name__ == '__main__':
    main()
