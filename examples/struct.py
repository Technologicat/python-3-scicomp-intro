# Python has no "struct", by design.
#
# If you need a data structure with named fields, use a class.
#
# This is easy to do, it doesn't need much beside the fields:

class MyData:
    z = 42  # static member, common for all instances of MyData

    def __init__(self, x, y):  # constructor
        # instance members
        self.x = x  # RHS is the x passed as argument, LHS names the field to store it in.
        self.y = y

##########################################
# usage examples

# store some data
m1 = MyData(2, 3)       # this calls the constructor (__init__) and returns the created object instance.
m2 = MyData(x=5, y=17)  # passing arguments by name is also fine (then order does not matter)

print(MyData.z)  # 42; static members can be accessed as ClassName.membername
print(m1.z)      # 42
print(m2.z)      # 42; a single copy of z is shared across all instances of MyData

print(m1.x)      # 2
print(m2.x)      # 5

try:
    print(MyData.x)  # AttributeError, does not exist since x is an instance member
except AttributeError as err:
    print(err)