#!/usr/bin/env racket
#lang sweet-exp racket

define uniqify(L)
  define seen null
  define unique?(x)
    cond [(not member(x seen)) set!(seen cons(x seen)) #t]
         [else #f]
  filter unique? L

define L '(2 1 2 1 3 3 3 4)
uniqify L
