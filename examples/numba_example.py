import numba

# reference pure-Python implementation
#
def f1(N):
    return sum( (n for n in range(N)) )

# Numba's nopython mode (as of v0.30.1) doesn't support list/dict/set comprehensions
# or generators, so we must do this the old-fashioned way instead:
#
def f2(N):
    acc = 0
    for j in range(N):
        acc += j
    return acc

# Same function, decorated with @numba.jit.
#
# This will get compiled when called for the first time.
#
@numba.jit
def f3(N):
    acc = 0
    for j in range(N):
        acc += j
    return acc

# This is equivalent.
#
# Calling f4() for the first time will compile the code.
# Any subsequent calls use the compiled version.
#
f4 = numba.jit(f2, nopython=True)

N = int(1e6)
assert f1(N) == f2(N) == f3(N) == f4(N)
