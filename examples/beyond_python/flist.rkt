#!/usr/bin/env racket
#lang sweet-exp racket

;; 0*x, 1*x, ..., (n-1)*x
define mul-upto(n)
  for/list ( [i in-range(n)] )
    λ (x) {i * x}

;; f0(x), f1(x), ..., f{n-1}(x)
define apply-flist(flist x)
  map (λ (f) f(x)) flist

module+ main
  define K mul-upto(5)
  apply-flist(K 10)
  ;
  define f list-ref(K 3)  ; Python: f = K[3]
  f(4)
