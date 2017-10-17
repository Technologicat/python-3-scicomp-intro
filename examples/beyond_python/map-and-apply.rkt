#!/usr/bin/env racket
#lang sweet-exp racket

;; Some exercises in map and apply: making equivalents for Python's zip() and enumerate().

;; Scheme                 Python
;;
;; (apply f L)            f(*L)
;; (map f L)              [f(x) for x in L]  # f const., x varies
;; (map f L1 L2)          [f(x,y) for x,y in zip(L1,L2)]  # etc. for n lists
;; (map (λ (f) (f x)) L)  [f(x) for f in L]  # x const., f varies

;; f0(x), f1(x), ..., f{n-1}(x)
define apply-flist(flist x)
  map (λ (f) f(x)) flist

;; equal-length lists only
;;
;; apply proc v ... lst
;;   - argument list of proc starts with the argument(s) v ...
;;   - the elements of lst will be unpacked to the end of the argument list
;;   - then proc is called with this argument list
;;
define zip-equal(. x)  ; varargs
  apply map list x     ; map list x1 x2 x3 ...

;; equivalent definition as a lambda:
;;
;; Note:
;;   λ x    puts the whole argument list into x
;;   λ (x)  makes a one-argument function
;;
;define zip-equal (λ x (apply map list x))

;; terminate on shortest input (like Python's)
;;
;; purely functional version, no mutable variables
;;
define zip(. x)
  let loop ([acc null]
            [lst x])
        define newacc (cons (map car lst) acc)
        define rest   (map cdr lst)
        cond [{(apply min (map length rest)) > 0} (loop newacc rest)]
             [else (reverse newacc)]

;; terminate on shortest input (like Python's)
;;
;; version using a mutable accumulator
;;
;define zip(. x)
;  let loop ([acc null]
;            [lst x])
;        define first (map car lst)
;        define rest  (map cdr lst)
;        set! acc (cons first acc)
;        cond [{(apply min (map length rest)) > 0} (loop acc rest)]
;             [else (reverse acc)]

;; like Python's, but no start parameter
;;
define enumerate-from-0(x)
  let loop ([count 0]
            [acc null]
            [lst x])
        define newacc (cons (list count (car lst)) acc)
        define rest   (cdr lst)
        cond [{(length rest) > 0} (loop {count + 1} newacc rest)]
             [else (reverse newacc)]

;; like Python's
;;
define enumerate(x . args)
  define start
    cond [{(length args) > 0} (list-ref args 0)]  ; if present, args[0] is start
         [else 0]
  let loop ([count start]
            [acc null]
            [lst x])
        define newacc (cons (list count (car lst)) acc)
        define rest   (cdr lst)
        cond [{(length rest) > 0} (loop {count + 1} newacc rest)]
             [else (reverse newacc)]


define a list(1 2 3)
define b list(4 5 6)
define c list(7 8 9)
define d list('a 'b)

zip-equal(a b c)
zip(a b d)

;; zip is its own inverse:
apply zip zip(a b c)  ; we must apply the outer zip, since the inner zip returns a list.
                      ; Also in Python, to do this, we need zip(*zip(a,b,c)).

define e list('a 'b 'c 'd 'e)
enumerate(e)
