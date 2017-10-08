# The Bunch pattern, or how to create an object that has the keys from a dict as field names.
#
# This is especially convenient when loading a huge number of arrays from a MATLAB file;
# Python will never inject them to the current namespace (à la MATLAB); instead,
# you will get a dictionary mapping array names (as strings) to the actual data
# (as NumPy arrays).
#
# Using a Bunch converts the strings into field names of an object instance,
# requiring less code to retrieve the data.


# At 3 lines of code, maybe the most compact implementation.
#
# This is based on the fact that self.__dict__ stores the mapping,
# from an object's attribute names, to the actual attributes.
# It is just a dictionary like any other.
#
# Basically, we insert any keys from adict not already present in self,
# and overwrite any matching keys. See help(dict.update) .
#
class Bunch:
    def __init__(self, adict):
        self.__dict__.update(adict)

##########################################
# Alternative version.

# This is equivalent, up to a slight difference in call syntax.
#
# We inject attributes into the namespace of the object instance by using setattr().
#
class AlsoBunch:
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

##########################################
# usage examples

# Create some test data for demonstration.
#
# In Python, identifiers - including field names of classes - must be strings,
# but they can be Unicode (roughly speaking, "alphabetical" characters are OK).
#
import math
D = {"answer": 42,
     "banana": "fruit",
     "π": math.pi }


# Create the bunch.
#
b1 = Bunch(D)
b2 = AlsoBunch(**D)  # does the same thing

# The data can now be accessed like this:
#
print(b1.answer)
print(b1.banana)
print(b1.π)