#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""How to implement a simple timer for use with the context manager.

Can be used for manual performance benchmarking of any desired part of code.

Created on Tue Feb  6 14:29:52 2018

@author: jje
"""

import time

class SimpleTimer:
    def __init__(self, label="", n=None):
        self.label = label
        self.n     = n      # number of repetitions (for averaging)

    # this runs when the "with" block is entered
    def __enter__(self):
        self.t0 = time.time()
        return self  # this return value goes into the "as s" below

    # this runs when the "with" block exits
    def __exit__(self, errtype, errvalue, traceback):
        dt         = time.time() - self.t0
        identifier = ("%s" % self.label) if len(self.label) else "time taken: "
        avg        = (", avg. %gs per run" % (dt/self.n)) if self.n is not None else ""
        print( "%s%gs%s" % (identifier, dt, avg) )


# Usage example

def do_stuff():
    time.sleep(0.001)    # simulate a workload by waiting a millisecond

def main():
    print("Benchmarking do_stuff():")

    with SimpleTimer(label=("    done in ")) as s:
        do_stuff()

    reps = 100
    with SimpleTimer(label=("    %d reps done in " % (reps)), n=reps) as s:
        for k in range(reps):
            do_stuff()

if __name__ == '__main__':
    main()
