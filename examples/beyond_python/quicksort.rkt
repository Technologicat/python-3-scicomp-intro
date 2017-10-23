#!/usr/bin/env racket
#lang sweet-exp racket

; For non-CS readers:
;  https://en.wikipedia.org/wiki/Quicksort
;
; The Racket standard library comes with  sort,  so there is no point in actually using this module.
; The purpose is to demonstrate how to write an easy-ish standard algorithm in Racket.

; Median-of-3 pivot.
define pivot!(v lo hi)
  define swap!(i1 i2)
    define tmp vector-ref(v i2)
    vector-set! v i2 vector-ref(v i1)
    vector-set! v i1 tmp
  define mid truncate{{lo + hi} / 2}
  cond [{vector-ref(v hi)  < vector-ref(v lo)}  swap!(lo hi)]
       [{vector-ref(v mid) < vector-ref(v lo)}  swap!(mid lo)]
       [{vector-ref(v hi)  < vector-ref(v mid)} swap!(hi mid)]
  vector-ref(v mid)

; Fat partition (Bentley and McIlroy).
;
; left  = start index of piv in v
; right = end index of piv in v (inclusive)
define partition!(v p lo hi)
  define low  empty
  define piv  empty
  define high empty
  for ([i in-range(lo {hi + 1})])
    define x vector-ref(v i)
    cond [{x < p} set!(low  (cons x low))]
         [{x > p} set!(high (cons x high))]
         [{x = p} set!(piv  (cons x piv))]  ; piv contains only values equal to p, so it's sorted
  define left  {lo + (length low)}          ; lo = start index of this slice in v
  define right {left + {(length piv) - 1}}
  vector-copy! v lo list->vector(`(,@low ,@piv ,@high))  ; see quasiquote, unquote-splicing
  values(left right)  ; multiple return values

; The recursive sort routine.
define qsort!(v lo hi)
  cond [{lo < hi}
        define(p pivot!(v lo hi))
        define-values((left right) partition!(v p lo hi))  ; catch multiple return values
        qsort!(v lo {left - 1})
        qsort!(v {right + 1} hi)]

; To save memory, we could check which of the two parts is shorter, do that first, and tail-recurse
; into the longer part (Sedgewick 1978), but we have chosen to keep things simple.
;
; (Scheme optimizes tail calls so that they won't grow the call stack.)

; Interface routine.
;
; Note that the algorithm is implemented in an imperative manner,
; but to the outside, this interface behaves like a pure function;
; the original L is not modified.
;
; This is far from optimal memory-wise; O(n) extra storage is required
; for v, and for constructing the return value as a list.
;
define quicksort(L [lo 0] [hi -1])  ; note syntax for default values
  define v list->vector(L)
  cond [{hi = -1} set!(hi {(vector-length v) - 1})] ; convenience
  qsort!(v lo hi)
  vector->list(v)

; conditional main, like in Python
;
; https://docs.racket-lang.org/guide/Module_Syntax.html
;
module+ main
  define L '(2 1 5 3 4 8 9 7 6 0)
  L
  quicksort(L)
