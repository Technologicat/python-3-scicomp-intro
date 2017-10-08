# In Python, (pretty much) everything is an object.

# For example, let's create an integer:
#
i = 42

# i is an int
cls = type(i)
print(cls)  # <class 'int'>
print(isinstance(i, cls))  # True, i is an int
print(isinstance(i, object))  # also True, everything inherits from "object"

# Even *types of objects* are objects:
cls_of_cls = type(type(i))
print(cls_of_cls)  # <class 'type'>
print(isinstance(cls, cls_of_cls))  # True, int is a type

# For some examples of what this allows to do, see bunch.py and monkey_patching.py.

##########################################
# Advanced

# Just out of curiosity, what attributes does an "int" have?
#
# dir(obj): "directory" of obj; see help(dir)
#
print(dir(cls))

# We see that an "int" mainly has magic methods that implement arithmetic:
# __abs__, __add__, __sub__, __mul__, __truediv__, __floordiv__, __pow__, ...
#
# The __r*__ versions (e.g. __rmul__) "operate from the right".
#
# When Python sees
#   a*b
# it will first try
#   a.__mul__(b)
# and if that is not supported (and a and b are of different types), then
#   b.__rmul__(a)
#
# This is distinct from __mul__ so that we get the correct result also if the
# multiplication happens to be non-commutative for the objects in question.
# (In this case, b needs to know it is on the right; Python supplies this
#  information by calling b.__rmul__() instead of b.__mul__().)
#
# https://stackoverflow.com/questions/5181320/under-what-circumstances-are-rmul-called
