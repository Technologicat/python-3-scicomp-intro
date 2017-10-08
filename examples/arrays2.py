import numpy as np

#####################################
# Creating NumPy arrays


# empty: uninitialized memory
#
# - useful if you are immediately going to write into all elements anyway.
#
# - data type (dtype) must be specified. Usually:
#   - np.float64 = IEEE-754 double = C double = MATLAB default = Fortran REAL*8
#   Others:
#   - np.complex128 = C double complex = MATLAB default complex = Fortran COMPLEX*16
#   - np.int64 = 64-bit integer. Useful for index arrays.
#   - np.int32 = 32-bit integer. Saves memory if you're sure you don't need any
#                                values larger than 2**31 - 1 = 2 147 483 647.
#
# shape:
#
# 1D: (n,)
# 2D: (m, n): rows, cols
# 3D: (k, m, n)
# ...
#
A = np.empty((5,5), dtype=np.float64)
A[:,:] = 3  # fill the whole array with threes
            # (the RHS will be automatically converted into the array dtype)
print(A)

# array filled with zeroes
#
B = np.zeros((5,5), dtype=np.float64)

# array filled with ones
#
C = np.ones((5,5), dtype=np.float64)


# initialize array from Python list
#
# - 1D array = list of numbers.
# - Items *must* be separated by a comma (not only whitespace).
#
x = np.array( [1, 2, 3], dtype=np.float64 )

# - 2D array = list of lists.
#
# - Unlike in MATLAB:
#   - There is no separate "row separator" like MATLAB's ;
#   - Each row is a Python list.
#   - These lists are just items in the outer list.
#     - The outer list is the "list of rows".
#     - Hence also rows are separated by a comma.
#
M = np.array( [ [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9] ], dtype=np.float64 )


# NumPy array to Python list:
#
N = M.tolist()


# initialize array by copying an existing array
#
K = np.array( M )
L = M.copy()  # np.arrays also have a copy() method, maybe makes your code more readable

# See also:
#  - np.empty_like(), np.zeros_like(), np.ones_like()
#  - copy shape and dtype, fill with what the function name suggests
#
P = np.zeros_like(M)  # same shape and dtype as M, but filled with zeroes


# DANGER: this makes just an alias for the same object instance
#
V = M
print( V is M )  # True


#####################################
# views

# In NumPy, most slicing operations create a *view* to the original data.
#
# (If you want a copy, make one explicitly.)
#
V = M[:,2]  # third column of M (remember 0-based indexing)
print(V)
print(M)
V[2] = 100  # this modifies the data in M
print(V)
print(M)


# linear view into M (a.k.a. linearly indexed view, one-subscript view)
#
W = M.reshape(-1)  # -1 = count number of elements automatically
print( W.shape )


# this is valid, because the input is a scalar
#
M[:] = 4  # fill M with fours

# but this is an error due to shape mismatch:
#
R = np.arange(9)  # [0,1,2,3,4,5,6,7,8]
try:
    print("This will cause a ValueError:")
    M[:] = R  # ValueError!
except ValueError as e:
    print(e)

# solution a), use the linear view:
#
W[:] = R  # OK!

# solution b), reshape the input:
#
M[:,:] = np.reshape(R, M.shape)  # OK!


#####################################
# singleton dimensions

# = dimensions with length 1

# inserting/suppressing singleton dimensions helps to unify indexing operations
# in code that must support both NumPy arrays and scalars:
#
P = np.atleast_1d( 42.0 )  # scalar --> 1D array of one element
print(P)
# also np.atleast_2d(), np.atleast_3d()

p = np.squeeze(P)          # --> back to scalar
print(p)


#####################################
# multidimensional indexing

# Getting a subarray is different from MATLAB:
#
I = np.array( (0,1,2), dtype=int )  # rows
J = np.array( (1,2), dtype=int )    # columns
try:
    print("This will cause an IndexError:")
    print( M[I,J] )      # IndexError!
except IndexError as e:
    print(e)

# To do that, use np.ix_():
#
print( M[np.ix_(I,J)] )  # OK! (array containing columns 1,2 from rows 0,1,2 of M,
                         #      like MATLAB's M(I,J))


# Indexing a multidimensional array by vectors means something different in NumPy:
#
# M[I[0],J[0]], M[I[1],J[1]], ...
#
I = np.array( (0,2), dtype=int )  # rows
J = np.array( (1,2), dtype=int )  # columns
print( M[I,J] )  # OK! -->[ M[0,1], M[2,2] ]


#####################################
# some matrices

# identity matrix
#
# note: no shape tuple, always 2D and square
#
I = np.eye(5, dtype=np.float64)  # shape (5,5)
print(I)

# diagonal matrix
#
# - the input is a 1D array to put onto the diagonal
#
D = np.diag( np.arange(10) )
print(D)

# - the same function, np.diag(), also extracts the diagonal from a 2D array
#   if given 2D input
#
d = np.diag(D)
print(d)


# tridiagonal matrix (from the 1D laplacian)
#
n = 10
d = -2 * np.ones( (n,), dtype=np.float64 )
s = np.ones( (n-1,),  dtype=np.float64 )
d = np.diag(d)      # main diagonal
u = np.diag(s, +1)  # upper subdiagonal
l = np.diag(s, -1)  # lower subdiagonal
T = l + d + u       # summing arrays elementwise
print(T)


#####################################
# sparse matrices

# Create a sparse matrix.
#
# (dr[k],dc[k],data[k]) is the kth nonzero matrix element.
#
import scipy.sparse
dr   = (0, 1, 4)  # row
dc   = (3, 2, 4)  # column
data = (1, 2, 3)
S = scipy.sparse.coo_matrix( (data, (dr,dc)), shape=(5,5), dtype=np.float64 )
S = S.tocsr()   # convert to a format that's efficient to compute with
                # (for some operations, CSR is good; for others, CSC)

print(type(S))  # it's now a scipy.sparse.csr.csr_matrix
print(S)


# Can also convert dense to sparse:
#
A_dense  = np.random.random( (3,3) )
A_sparse = scipy.sparse.csr_matrix(A_dense)


# Solve a sparse linear equation system.
#
n = 10
A = scipy.sparse.random(n, n, density=0.1, format='coo') + scipy.sparse.eye(n)
b = np.random.random(n)
x = scipy.sparse.linalg.spsolve(A,b)

# Plot the sparsity pattern
#
import matplotlib.pyplot as plt
plt.figure(1)
plt.clf()
plt.spy(A)
plt.show()
