# This expands the example from duck_typing.py.

class Duck:
    def quack(self):
        print( "quack quack" )

class AustralianSpottedDuck(Duck):
    pass  # we inherit quack() from ancestor

class AnimalSimulator3000:  # NOTE: no relation to Duck
    def meow(self):
        print( "meow" )

    def quack(self):
        print( "quack" )

class NotADuck(object):
    pass

class NotInitiallyADuck:
    def duckify(self):
        """Monkey patch self to add quack()."""

        # In Python, functions can be defined anywhere.
        #
        def f(self):
            print( "quack quack quack" )

        # To create a method at runtime, we setattr() our "f" into the class object,
        # which describes what objects of this class can do.
        #
        # - "f" is the name in the local scope, whereas the attribute name
        #   will be "quack".
        # - The name "f" has no meaning other than, that in the local scope here,
        #   it points to the function (object instance!) we created.
        #
        # In Python, there are no private attributes; it is left to the programmer
        # to use this power responsibly.
        #
        setattr(self.__class__, 'quack', f)

a = Duck()
b = AustralianSpottedDuck()
c = AnimalSimulator3000()
d = NotADuck()

a.quack()   # OK
b.quack()   # OK
c.quack()   # OK
try:
    d.quack()  # AttributeError!
except AttributeError as err:
    print(err)

e = NotInitiallyADuck()
try:
    e.quack()  # AttributeError!
except AttributeError as err:
    print(err)
e.duckify()
e.quack()   # now OK
