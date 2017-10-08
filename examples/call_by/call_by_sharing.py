# -*- coding: utf-8 -*-

def f(r):
    r = 42  # only rebinds the name "r" in the local scope

def main():
    a = 23
    f(a)
    print(a)  # still 23

if __name__ == '__main__':
    main()

