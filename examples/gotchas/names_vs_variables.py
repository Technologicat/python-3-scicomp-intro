# Python has no variables in the classical sense.
#
# Instead, *names* are labels that point to object instances.
#
# See also:
#
# Ned Batchelder: Facts and myths about Python names and values
# https://nedbatchelder.com/text/names.html

L = [1, 2, 3]  # create a list
print(L)

# Observe what happens:
#
K = L
K.append(4)

print(K)
print(L)  # what happened here?

# Modifying K modified also L, because K is just another name pointing
# to the same object instance.
#
# The operator "is" tests object identity:
#
print(K is L)  # True, it's the same object

# To create an independent copy, make one explicitly:
#
M = L.copy()   # RHS creates and returns the copy, LHS gives it a name
print(M is L)  # False, it's a different object

# Now we can:
M.append(5)
print(M)
print(L)  # not modified


# Instances of primitive types, such as int, are immutable.
#
i = 23
j = i
print(j is i)  # True, it's the same object

i += 1  # same as i = i + 1
print(j is i)  # False, "i" now points to a new object instance,
               # which has value j+1.