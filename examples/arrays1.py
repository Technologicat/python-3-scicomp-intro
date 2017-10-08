import numpy as np

#####################################
# Arithmetic

# Primitive operations are *always* elementwise:
#
u = np.arange(3)
v = np.arange(3)

print( u+v )
print( u*v )   # MATLAB  u .* v

# Exponentiation is denoted by **
#
print( u**2 )  # MATLAB  u.^2


#####################################
# Linear algebra

n = 3
A = np.random.random( (n,n) )
b = np.random.random(n)

print( A.shape )     # (3,3); NumPy "shape" == MATLAB "size"
print( A.shape[0] )  # number of rows
print( A.shape[1] )  # number of columns
print( A.size )      # total number of elements
print( A.ndim )      # number of array dimensions = tensor rank

# Rank, in the sense of linear algebra (computed via SVD):
#
print( np.linalg.matrix_rank(A) )

# Dot product
#
print( np.dot(A,b) )
print( A.dot(b) )
#print( A @ b )  # Python 3.5 and later


# Solve linear equation system
#
x = np.linalg.solve(A,b)  # MATLAB  x = A \ b
