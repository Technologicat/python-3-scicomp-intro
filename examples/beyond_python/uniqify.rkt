#!/usr/bin/env racket
#lang sweet-exp racket

;; If we use filter, we must store the seen status of each item as a side-effect,
;; because filter only feeds its predicate one item at a time, and expects only
;; a boolean as output (so there is no easy way to pass state in a functional style).
;;
;; Hence, this is somewhat imperative, but the code is very short.
;;
define uniqify(L)
  define seen null
  define unique?(x)
    cond [(not member(x seen)) set!(seen cons(x seen)) #t]
         [else #f]
  filter unique? L

;; Functional style:
;;   - state is passed as parameters
;;   - tail recursion
;; We filter manually.
;;
define uniqify2(L)
  let keep-if-unique ([input L]
                      [seen null]
                      [output null])
    cond [(empty? input) reverse(output)]  ; done
         [else
            define(x car(input))
            define(the-rest cdr(input))
            cond(
              [(not member(x seen)) keep-if-unique(the-rest (cons x seen) (cons x output))]
              [else keep-if-unique(the-rest seen output)])]

module+ main
  define L '(2 1 2 1 3 3 3 4)
  uniqify L
  uniqify2 L
