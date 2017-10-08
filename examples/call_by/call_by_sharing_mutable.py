# -*- coding: utf-8 -*-

def f(L):
    L[0] = 42  # modifies the contents of object L, which is shared by the caller and the callee

def main():
    a = [23]  # make a list of one element
    f(a)
    print(a)  # [42]

if __name__ == '__main__':
    main()

