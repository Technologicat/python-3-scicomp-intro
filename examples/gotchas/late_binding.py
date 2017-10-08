# Python's closures are late-binding.
#
# Or in plain(er) English:
#  - closure      = Anonymous function + information about the scope it had
#                   when it was created. This includes information about names
#                   that were visible at that time.
#  - late binding = Value lookup (by name) occurs when the function is *called*,
#                   not when it was defined.

def problem():
    funcs = [ lambda x: i*x for i in range(5) ]

    # apply each func to x=2 and print result
    #
    y = [ f(2) for f in funcs ]
    print(y)  # [8, 8, 8, 8, 8]

    # The problem is that there is only one name "i" in the list comprehension.
    # Each of the lambdas captures this same "i".
    #
    # When the loop has finished, "i" has the value 4. This is what all the
    # lambdas see.

def solution1():
    # idiom sometimes known as "fake default"
    #
    # utilize the fact that default values for function arguments bind at definition time.
    #
    funcs = [ lambda x,j=i: j*x for i in range(5) ]

    # OK!
    y = [ f(2) for f in funcs ]
    print(y)  # [0, 2, 4, 6, 8]

    # But fails if the caller supplies extra arguments, since then the default is not used:
    y = [ f(2,3) for f in funcs ]
    print(y)  # [6, 6, 6, 6, 6]

def solution2():
    # function factory
    #
    # We define another function that the loop must call to create the lambda.
    # This function sees only the *value* of i at the time it is called.
    #
    def make_f(j):
        return lambda x: j*x

    funcs = [ make_f(i) for i in range(5) ]

    # OK!
    y = [ f(2) for f in funcs ]
    print(y)  # [0, 2, 4, 6, 8]

    # The previous hole has been plugged, since now the lambdas do not allow any extra arguments.

def solution2_shorter1():
    # we may also define the function factory using a lambda:
    make_f = lambda j: lambda x: j*x   # same as lambda j: (lambda x: j*x)
    funcs  = [ make_f(i) for i in range(5) ]

    # OK!
    y = [ f(2) for f in funcs ]
    print(y)  # [0, 2, 4, 6, 8]

def solution2_shorter2():
    # In the lambda format, the function factory can also be inlined
    # into the list comprehension.
    #
    # This gives us an *anonymous* function factory.
    #
    funcs = [ (lambda j: lambda x: j*x)(i) for i in range(5) ]

    # OK!
    y = [ f(2) for f in funcs ]
    print(y)  # [0, 2, 4, 6, 8]

def solution3():
    # use the functional programming technique known as
    # partial application (of function arguments)
    #
    from functools import partial

    def f(j,x):
        return j*x

    # partial(f, i) returns, in effect, lambda x: f(j=i, x)
    #
    funcs = [partial(f, i) for i in range(5)]

    # OK!
    y = [ f(2) for f in funcs ]
    print(y)  # [0, 2, 4, 6, 8]

def solution3_shorter():
    # our f() is just a multiplication, so we can get it from the standard library.
    #
    # The module "operator" defines named function versions of operators
    # (such as the arithmetic operators), exactly for use cases like this.
    #
    from functools import partial
    from operator import mul  # mul(a,b) is the same as a*b

    funcs = [partial(mul, i) for i in range(5)]

    # OK!
    y = [ f(2) for f in funcs ]
    print(y)  # [0, 2, 4, 6, 8]


problem()
solution1()
solution2()
solution2_shorter1()
solution2_shorter2()
solution3()
solution3_shorter()