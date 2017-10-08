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
