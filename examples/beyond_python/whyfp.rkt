#lang sweet-exp racket

;; Some racketified examples based on:
;; http://www.cse.chalmers.se/~rjmh/Papers/whyfp.pdf

;; foldr
define reduce(f x lst)
  match lst
    '() x
    (cons a l) (f a (reduce f x l))

;; foldl
define reducel(f x lst)
  let loop ([acc x]
            [l lst])
    match l
      '() acc
      (cons a k) (loop (f a acc) k)

;; Compare the traditional lispy solutions:

;define reducer(f x lst)
;  cond
;    empty?(lst)
;      x
;    else
;      f (car lst) (reducer f x (cdr lst))

;define reducel(f x lst)
;  let loop ([acc x]
;            [l lst])
;    cond
;      empty?(l)
;        acc
;      else
;        loop (f car(l) acc) cdr(l)

;; map is really just "reduce (compose cons f) empty", but Racket is not Haskell, so...

;; adaptors to fit an arity-1 function into an arity-2 compose chain
define ->1(f) (λ (a b) (values (f a) b))
define ->2(f) (λ (a b) (values a (f b)))

define map(f lst)
  reduce (compose cons (->1 f)) empty lst

define map2(f)  ; point-free style: return a function that accepts a list
  curry reduce (compose cons (->1 f)) empty

;; ...but PFS really looks better with currying.
;; This version either returns a function (if args empty), or applies immediately.
define map3(f . args)
  apply curry reduce (compose cons (->1 f)) empty args

define append(a b)
  reduce cons b a

define append2(a b)
  foldr cons b a

define reverse
  curry foldl cons empty

define append3(a b)
  foldl cons b reverse(a)

define append4(a b)
  reducel cons b reverse(a)

define sum
  curry reduce + 0

define product
  curry reduce * 1

module+ main
  define a '(1 2)
  define b '(3 4)
  define c '(1 2 3)
  sum a
  product b
  append a b
  append2 a b
  append3 a b
  append4 a b
  define sqr(x) {x * x}
  map sqr c
  (map2 sqr) c
  map3 sqr c
  (map3 sqr) c
;  reducer cons empty c  ; just copies c
