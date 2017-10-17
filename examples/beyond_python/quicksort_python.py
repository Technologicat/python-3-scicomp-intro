#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# For non-CS readers:
#  https://en.wikipedia.org/wiki/Quicksort
#
# The Python standard library comes with sorted(), so there is no point in actually using this module.
# The purpose is to demonstrate how to write an easy-ish standard algorithm in Python.

# Median-of-3 pivot.
#
# https://stackoverflow.com/questions/7559608/median-of-three-values-strategy
#
def _pivot(L, lo, hi):
    def swap(i1, i2):
        L[i1],L[i2] = L[i2],L[i1]

    mid = (lo+hi)//2

    # Sort the lo/mid/hi values in the array and return the middle one;
    # it is then the median.
    #
    # In this implementation, it doesn't matter if some of the lo/mid/hi
    # indices are the same, as we swap the actual original data elements.
    #
    # (This matters if we wanted to split the logic to a separate "sort3".
    #  In the example array below, then, near the end of the sorting,
    #  some duplicate indices will arise, leading to incorrect overwrites
    #  if we just L[lo],L[mid],L[hi] = sort3(L[lo],L[mid],L[hi]).)
    #
    if L[hi] < L[lo]:
        swap(lo,hi)
    if L[mid] < L[lo]:
        swap(mid,lo)
    if L[hi] < L[mid]:
        swap(hi,mid)

    return L[mid]

# Fat partition (Bentley and McIlroy).
#
# https://en.wikipedia.org/wiki/Quicksort#Repeated_elements
#
def _partition(L, p, lo, hi):
    low  = []
    piv  = []
    high = []
    for x in L[lo:hi+1]:
        if x < p:
            low.append(x)
        elif x > p:
            high.append(x)
        else: # x == p:
            piv.append(x)

    left  = lo + len(low)  # lo = start index of this slice in L
    right = left + len(piv) - 1

    # update L
    tmp = low  # low no longer needed, doesn't matter that this just creates a name
    tmp.extend(piv)
    tmp.extend(high)
    L[lo:hi+1] = tmp

    # return the start and end (inclusive) indices of the pivot part in L
    return left,right

# The recursive sort routine.
#
def _qsort(L, lo, hi):
    if lo < hi:
        p = _pivot(L, lo, hi)
        left,right = _partition(L, p, lo, hi)
        _qsort(L, lo, left-1)
        _qsort(L, right+1, hi)

# Interface routine.
#
def quicksort(L, lo=0, hi=-1):
    if hi == -1:  # convenience
        hi = len(L) - 1

    tmp = L.copy()
    _qsort(tmp, lo, hi)
    return tmp

def main():
    L = [2, 1, 5, 3, 4, 8, 9, 7, 6, 0]
    print(L)
    print(quicksort(L))

if __name__ == '__main__':
    main()

