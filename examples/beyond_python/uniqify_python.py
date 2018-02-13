#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def uniqify_oneliner(L):  # CAUTION: generally considered unreadable in the Python community
    return (lambda seen: [seen.add(x) or x for x in L if x not in seen])(set())

def uniqify_modern(L):
    seen = set()
    return (seen.add(x) or x for x in L if x not in seen)

def uniqify_classic(L):
    seen = set()
    def isunique(x):
        if x not in seen:
            seen.add(x)
            return True
        else:
            return False
    return (x for x in L if isunique(x))  # equivalent with filter(isunique, L)

L = (2, 1, 2, 1, 3, 3, 3, 4)
print(tuple(uniqify_oneliner(L)))
print(tuple(uniqify_modern(L)))
print(tuple(uniqify_classic(L)))

