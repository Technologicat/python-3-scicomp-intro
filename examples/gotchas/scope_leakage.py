# - In Python, the smallest unit of scope is the function.
# - A for loop does not introduce its own scope; it uses the surrounding scope.
# - Hence, loop variables "leak" into the surrounding scope.
#
# - List comprehesions are a special case; for them, the loop variable
#   exists only in the list comprehension. (In this respect, Python 3
#   treats list comprehensions as if they were functions.)

def f1():
    i = 100  # create local name i, bind it to value 100
    L = []   # create empty list
    for i in range(5):
        L.append(i)
    print(i)  # 4, last value from loop; original name i was overwritten

def f2():
    i = 100
    L = [i for i in range(5)]  # list comprehension, does not leak
    print(i)  # 100

f1()
f2()

