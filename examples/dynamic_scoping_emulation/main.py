# This example continues from lexical_scoping.py.
#
# From Wikipedia:
#    https://en.wikipedia.org/wiki/Scope_(computer_science)#Lexical_scoping_vs._dynamic_scoping
#
# In *lexical scoping*, if a variable name's scope is a certain function,
# then its scope is the program text of the function definition:
# within that text, the variable name exists, and is bound to the variable's
# value, but outside that text, the variable name does not exist.
#
# By contrast, in *dynamic scoping*, if a variable name's scope is a certain
# function, then its scope is the time-period during which the function is
# executing: while the function is running, the variable name exists, and
# is bound to its value, but after the function returns, the variable name
# does not exist.

# It is possible to emulate dynamic scoping in Python.
#
# This "dynscope" module is based on a StackOverflow answer by Jason Orendorff, 2010;
# examine it for details.
#
# https://stackoverflow.com/questions/2001138/how-to-create-dynamical-scoped-variables-in-python
#
from dynscope import env

def f():
    print(env.a)

def main():
    # The dynamic variables exist for the duration of this with block:
    #
    with env.let(a=2, b="foo"):
        print(env.b)  # prints "foo"
        f()  # call a function that uses env.a or env.b

    # Once the with block exists, the dynamic variables no longer exist.
    #
    try:
        print(env.b)
    except AttributeError as err:
        print(err)

main()