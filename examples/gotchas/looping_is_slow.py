import time
import numpy as np

n = int(1e6)

################################

t0 = time.time()
s = 0.0
for i in range(n):
    s += 1.0
dt = time.time() - t0
print("Explicitly sum in loop (%g terms): %gs" % (n, dt))

t0 = time.time()
s = sum( range(n) )
dt = time.time() - t0
print("Python builtin sum() (%g terms): %gs" % (n, dt))

print("NumPy:")
t0 = time.time()
L = np.arange(n, dtype=int)  # actual dtype will be np.int64
dt1 = time.time() - t0
print("    create array (%g terms): %gs" % (n, dt1))

t0 = time.time()
s = np.sum(L)
dt2 = time.time() - t0
print("    np.sum(): %gs" % (dt2))
print("    total %gs" % (dt1+dt2))

################################

A = np.empty( (n,), dtype=np.float64 )

t0 = time.time()
for i in range(n):
    A[i] = 42.0
dt = time.time() - t0
print("Write into array in loop (%g items): %gs" % (n, dt))


B = np.empty( (n,), dtype=np.float64 )

t0 = time.time()
B[:] = 42.0
dt = time.time() - t0
print("Write into array, vectorized (%g items): %gs" % (n, dt))

################################
