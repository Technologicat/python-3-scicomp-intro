# Beware of mutable default arguments.
#
# The definition of f() creates an empty list instance - exactly once - when the
# line with the def is executed. Then it sets *this list instance* as the
# default value of L.

def f(L=[]):  # don't do this!
    L.append(1)
    return L

print(f())  # [1]
print(f())  # [1, 1]
print(f())  # [1, 1, 1]