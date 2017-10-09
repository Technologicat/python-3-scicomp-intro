# Python uses lexical scoping, just like many other languages.

# From Wikipedia:
#    https://en.wikipedia.org/wiki/Scope_(computer_science)#Lexical_scoping_vs._dynamic_scoping
#
# In *lexical scoping*, if a variable name's scope is a certain function,
# then its scope is the program text of the function definition:
# within that text, the variable name exists, and is bound to the variable's
# value, but outside that text, the variable name does not exist.

# It doesn't matter where in that text the variable is created,
# as long as it is done first before calling any inner functions
# that use it:
#
def main():
    def f():
        # no "i" defined here.
        print("i = %d" % (i))

    # error, "i" does not exist yet
    print("This does not work:")
    try:
        f()
    except NameError as err:
        print(err)

    print("This works:")
    i = 3  # Now that we have defined "i"...
    f()    # ...it will be present in the inner function f().

main()

##########################################
# Advanced

# If you want your code to be evil, it is possible to emulate dynamic scoping.
# Code examples and explanation:

# https://stackoverflow.com/questions/2001138/how-to-create-dynamical-scoped-variables-in-python
# https://stackoverflow.com/questions/32699437/how-to-understand-dynamic-scoping-using-python-code
