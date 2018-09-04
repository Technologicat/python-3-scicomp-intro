#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Iterator protocol example.

How to make custom objects support iteration (as in for loops over them)
and the tuple unpacking syntax.
"""

# For more, see e.g.
#   https://www.programiz.com/python-programming/iterator
#
# See also collections.namedtuple, which already covers the basic use case.

class MyIterableType:
    def __init__(self, x1, x2, x3):
        self.x = x1
        self.y = x2
        self.z = x3

    def __iter__(self):
        return MyIterator(self)

class MyIterator:
    def __init__(self, target):
        self.target = target  # object instance being iterated over
        self.fields = ("x", "y", "z")
        self.idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx < len(self.fields):
            value = getattr(self.target, self.fields[self.idx])
            self.idx += 1
            return value
        else:
            raise StopIteration()  # tell Python we're out of items

# We could just as well use this to (effectively) implement a generator:
class Squared:
    def __init__(self, start_from=0):
        self.k = start_from
    def __iter__(self):
        return self
    def __next__(self):
        value = (self.k)**2
        self.k += 1
        return value

# standard library namedtuple for usage comparison
from collections import namedtuple
MyOtherIterableType = namedtuple("MyOtherIterableType", ("x", "y", "z"))

def main():
    o1 = MyIterableType(1, 2, 3)
    o2 = MyOtherIterableType(1, 2, 3)

    for obj in (o1, o2):
        for x in obj:
            print(x)
        # Python uses the iterator protocol to perform tuple unpacking
        # on custom datatypes.
        a, b, c = obj
        print(a, b, c)

    ss = Squared()
    for _ in range(10):
        print(next(ss))

    # Maybe a slightly more elegant way to use it:
    #  - iterate directly over the iterator
    #  - use the terminate-on-shortest-input property of zip()
    #    to stop reading from the infinite iterator after 10 items
    print([s for s,_ in zip(Squared(), range(10))])

if __name__ == '__main__':
    main()
