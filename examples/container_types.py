#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Built-in types 2 of 2: container types.

#####################################
# list, tuple

# list  = Mutable ordered sequence of arbitrary items.
# tuple = Immutable version of list.

print("\n" + "=" * 30)
print("list\n")

L1 = [1, 2, 3, 4]  # lists are created using brackets []
L  = []            # empty list

L2 = [5, "foo", "bar", 3.14]  # items can be any object instances...
print(L1)
print(L2)

L3 = [L1, L2]                 # ..."any object instance" includes lists!
print(L3)
print(L3[0])     # first element of L3 (is L1)
print(L3[0][1])  # second element of the first element of L3 (is L1[1])

print(L1[0])     # element access: first element of L1 (remember 0-based indexing!)
print(len(L1))   # number of items


T1 = tuple(L1)  # copy list into a new tuple
print(T1[0])    # in all respects tuples are like lists, except that...
try:
    T1[0] = 23  # ...they are read-only
except TypeError as err:
    print(err)

# A tuple is useful when you know that a particular list will not change
# once created, and want Python to raise an error if your code accidentally
# writes into it. (*fail-fast principle*, makes it easier to create robust programs)
#
# Another use case is when you need something hashable (e.g. to use as an item
# in a set, or as a dictionary key). (NOTE: hashable ⇒ also immutable)


T2 = (3,4,5)    # tuples are created using parentheses ()
T3 = (10,)      # special case: one-item tuple (Python needs the comma to know
                #               that this is a tuple, not just a parenthesized
                #               expression)
T4 = ()         # empty tuple


# To Fortran and C users, this is an important point, so it bears repeating:
#
# Object instance can be anything, including list, dict, or set.
#
# --> so not necessarily just one object, but can be a collection of objects
#     (because the collection itself is just an object!)
#
# --> simple pythonic data structures
#
# This is especially useful for ad-hoc groupings of objects. If you notice a need
# for a more permanent grouping (e.g. across the whole run of your program),
# create a class and use it as a data structure with named fields. This is
# easy to do; see struct_as_class.py.
#
# (If you want to go all the way to object-oriented programming (OOP), feel free
#  to place also some algorithms in your class. *Methods* are functions that are
#  part of a class, and typically operate on the data stored in the object
#  instance. A lot has been written on OOP, but for simple cases it doesn't
#  need to be any more complicated than that.)

# To iterate over a list, for/in.
#
# (This works for any iterable, not just lists.)
#
for x in L1:
    print("x = %d, x**2 = %d" % (x, x**2))

L = []
L.append(10)  # add an item to the end
print(L)

L.extend(L1)  # add all items from another list to the end
print(L)

L.insert(1, "baz")  # insert item before given index
print(L)

x = L.pop(2)  # remove item at index 2 and return it
              # (if you don't need it, just "L.pop(2)" without assigning)
print(x)
print(L)

y = L.pop()   # remove last item and return it
print(y)
print(L)

# membership testing
#
# NOTE: O(n) search by walking the list, inherently slow for large lists.
#
# Lists are not meant for searching. If you need to search a large collection,
# consider a set or a dict instead, both of which give O(1) searching.
#
if 'baz' in L:
    print("'baz' is in list L")

L.remove("baz")  # search for and remove given item (this is also O(n))
print(L)

L.sort()  # sort in-place
print(L)

L.reverse()  # reverse in-place
print(L)

# If you want a sorted copy, while not changing the original,
# use the built-in function sorted() (instead of the sort() method
# of the list instance).
#
# This works with any iterable, not just lists.
#
L_sorted = sorted(L)
print(L_sorted)

# For a reversed copy, use reversed()...
#
L_reversed = reversed(L_sorted)

print(L_reversed)              # ...but it returns an iterator.
                               #
                               # This is good, because it doesn't need
                               # extra memory, it's fast to create,
                               # and it works just as well for iterating
                               # over the reversed collection (e.g. in a for loop).
                               #
                               # But what if you need an actual list?

L_reversed = list(L_reversed)  # Passing the iterator to the list constructor
                               # places all items from the iterator
                               # into a new list instance.

print(L_reversed)              # Now we have a list.


#####################################
# set, frozenset

# set       = Mutable unordered collection of unique hashable items.
# frozenset = Immutable version of set.

print("\n" + "=" * 30)
print("set\n")

S1 = {1, 2, 3}
S2 = {1, 1, 2, 3}  # duplicates get automatically discarded
print(S1)
print(S2 == S1)

S3 = set()  # empty set (NOTE: the notation {} instead means empty dict)

S = {'a', 'b', 'c'}
S.add('d')     # add an item
S.remove('c')  # remove an item
print(S)
print(sorted(S))  # if you want to copy into a sorted list for printing (useful in debugging)

# membership testing: in, not in
#
# (fast, O(1))
#
if 'a' in S:
    print("yes, 'a' is in set S")
if 'c' not in S:
    print("no, 'c' is not in set S")

# To iterate over a set (NOTE: no guarantee of the order the items will appear in)
for x in S:
    print(x)

# logical operations between sets
A = {1, 2, 3, 4}
B = {2, 3, 5}
print( A.union(B) )         # A ∪ B
print( A.intersection(B) )  # A ∩ B
print( A.difference(B) )    # A ∖ B
print( B.difference(A) )    # B ∖ A


# Immutable set: frozenset
#
# This is useful when you know the contents of a particular set will not change
# once created, and want Python to raise an error if your code accidentally
# writes into it.
#
# The constructor takes an iterable.
#
F1 = frozenset( (1,2,3) )  # create from tuple, OK
F2 = frozenset( {1,2,3} )  # create from set, also OK


#####################################
# dict (dictionary)

# Mutable unordered collection of key-value pairs.
#
# key   - arbitrary hashable object instance (NOTE: hashable ⇒ also immutable)
# value - arbitrary object instance

print("\n" + "=" * 30)
print("dict\n")

D = {}  # empty dict

D = {1: 42, 'banana': 'fruit', 'π': 3.14}  # {key: value, key: value, ...}
print(D)

# To insert an item, index the dict by the new key and assign:
D['foo'] = 'bar'
print(D)

# To overwrite, just index by an existing key and assign:
#
D['foo'] = 'quux'
print(D)

# To retrieve an item, index the dict by the key (this returns the value):
print(D['foo'])

# To remove an item and return it:
#
x = D.pop('foo')
print(D)

# To update from another dict:
#
# This inserts any new keys, and overwrites any items with with matching keys.
#
D2 = {'banana': 'yellow', 3: 'an integer', 'x': 'sometimes a variable'}
D.update(D2)
print(D)


# Trying to retrieve with a nonexistent key raises an exception:
#
try:
    x = D['meow']
except KeyError as err:
    print("no 'meow' in D")
    x = None  # or do whatever here

# Alternatively, you can:
#
if 'meow' in D:  # search the keys (fast, O(1))
    x = D['meow']
else:
    print("no 'meow' in D")
    x = None

# Using the *expression form of if*, this can be shortened to:
#
x = D['meow'] if 'meow' in D else None

# The try/except solution follows the modern EAFP paradigm, "Easier to Ask for
# Forgiveness than Permission".
#
# The second solution follows the classical LBYL ("Look Before You Leap") paradigm.


# You can also use the get() method, which just returns None if the key was not there.
#
# Note, however, that this approach cannot distinguish between these two cases:
#   - the key is not in the dict
#   - the key is in the dict, but the value corresponding to it is None
#
# (Or, in engineering terms, in-band signaling is generally a bad idea.)
#
x = D.get('meow')
print(x)  # None

# The get() method also takes an optional argument, which is the default value
# if the key is not there. As seen above, if not set, the default is None.
#
# This can be useful when using a dict as a counter - to count the number of
# occurrences of each value in a list. (But see collections.Counter, which
# already does this internally; using that more explicitly communicates
# your intention if you wanted to use a counter).
#
print(D.get('meow', 0))


# Example of a counter:
#
data = [1, 1, 1, 2, 3, 3, 4, 4, 4, 5, 6, 7, 7]

C = {}
for key in data:
    C[key] = C.get(key, 0) + 1
print(C)  # data value --> number of occurrences

# Using the ready-made counter from the standard library:
#
from collections import Counter
C2 = Counter(data)
print(C2)


# To iterate over a dict:
for k,v in D.items():
    print("key '%s' has value '%s'" % (k,v))

# - D.items() returns, essentially, a list of tuples [(key,value), (key,value), ...]
# - in each iteration of the for loop, we use *tuple unpacking* to assign
#   the items of the current tuple into the two loop counters k,v.
#
# (Strictly speaking, D.items() returns a dict_items object, that can be
#  iterated over as if it were a list of tuples.)

# To iterate over keys only:
for k in D.keys():
    print(k)
    print(D[k])  # the corresponding value
                 # (no need to check for KeyError; here we know key k exists)

# To iterate over values only:
for v in D.values():
    print(v)
    # no way to retrieve the key this value corresponds to
    #
    # (inherently impossible; consider that in the general case,
    #  there may be duplicates in the values, while keys are unique.)

# Create a dict for reverse lookup.
#
# - This requires that the values of the original dict are hashable,
#   so that they can be used as keys.
#
# - This also requires the values to be unique; otherwise just one of them
#   (essentially randomly) will get picked for reverse lookup.
#
# The mechanism we use to make this is a *dict comprehension*.
#
R = { v: k for k,v in D.items() }
print(R)
