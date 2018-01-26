#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imperative and functional programming paradigms."""

# Imperative
def imp_sum(lst):
    s = 0
    for x in lst:
        s = s + x  # mutable state: "s" is updated
    return s

# Functional
def func_sum(lst):
    def loop(acc, lst):  # each iteration gets a new "acc"
        if not len(lst):
            return acc
        else:
            first,*rest = lst
            return loop(acc + first, rest)
    return loop(0, lst)

L = tuple(range(10))
print(imp_sum(L))
print(func_sum(L))
