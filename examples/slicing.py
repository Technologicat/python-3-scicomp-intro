import numpy as np

# - Python and NumPy indexing is 0-based.
# - Indexing operator is [].


# Make a rank-1 array (1D array, vector) of integers from 0 to 9.
#
# - np.arange comes from NumPy
# - the effect is the same as list(range(10)), but the result will be
#   an np.array instead of of a Python list.
#
A = np.arange(10)


# - Slicing is start:stop:step, where stop is *non-inclusive*.
# - Unneeded elements of the slice may be omitted.

# From the second element onward:
print( A[1:] )

# Up to but not including the last element:
print( A[:-1] )

# Every other element, starting from the fifth element:
print( A[4::2] )

# Reversed:
print( A[::-1] )

# Write to every element:
A[:] = 42
print(A)


# Multidimensional slicing.
#
# Let's make a rank-3 array (3D array).
#
# For now, don't worry about the details, we will return to creating arrays later.
#
# Just note an object-oriented programming pattern:
#
# - np.arange() returns an np.array.
# - np.array instances have a reshape() method, which returns the reshaped array.
# - Thus, we may chain these to create a shape (3,3,3) array in one go.
# - This is a pretty common way to generate an n-dimensional array
#   of dummy data for tutorials.
#
B = np.arange(27).reshape(3,3,3)
print(B)

print( B[0,1,:]   )  # A : by itself means all elements from that axis, like in MATLAB and in Fortran.

print( B[...,2]   )  # ... inserts as many : as needed to complete the index tuple.
print( B[:,:,2]   )  # equivalent

print( B[1,...,0] )
print( B[1,:,0]   )  # equivalent


# Gotcha for MATLAB users:
#
# In Python, slicing is only allowed when indexing.
#
# If you insist on doing 0:5:100 MATLAB style, there is a dummy object np.r_ that you can index to do this:

print( np.r_[0:100:5] )

# But in Python, the standard way is:

print( range(0,100,5) )
print( np.arange(0,100,5) )  # in case you need it to be an np.array


# Also MATLAB-style linspace(start,stop,npoints) is fine.
#
# - In linspace(), the endpoint is inclusive!
#
# - Just like in MATLAB, we "fencepost" npoints to have the points spaced at intervals of 5.
#   20 intervals --> 21 points.
#
# - By default, linspace makes floats, so we explicitly tell it to make integers.

print( np.linspace(0,100,21, dtype=int) )


#################################################################
# Optional topic: some differences between NumPy and bare Python

# Observe what happens if we try the same slicing operations on a range():
#
A = range(10)
print( A[1:] )
print( A[:-1] )
print( A[4::2] )
print( A[::-1] )

# This creates new range objects, with appropriately adjusted parameters.

# Obviously, range does not support writing into it, since in the general case,
# the result would no longer be a range:
#
try:
    print("This will cause a TypeError:")
    A[:] = 42
except TypeError as e:
    print(e)  # show the error message, but otherwise ignore the error.


# How about a Python list?
#
L = list(range(10))
print( L[1:] )
print( L[:-1] )
print( L[4::2] )
print( L[::-1] )

# This works like the NumPy array.

# But when assigning to a slice of a list, the RHS must be an iterable
# containing the correct number of items.
#
# Hence, this does not work:
#
try:
    print("This will cause a TypeError:")
    L[:] = 42
except TypeError as e:
    print(e)

# We conclude that we have NumPy's *broadcasting rules* to thank for the fact
# that with a NumPy array, we can assign a scalar to a slice.
