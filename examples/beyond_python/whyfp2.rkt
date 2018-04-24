#lang sweet-exp spicy
;; Auto-currying teaching example language for Racket:
;; https://github.com/Technologicat/spicy

define foldl(f x lst)
  match lst
    '() x
    (cons a l) (foldl f (f a x) l)

define foldr(f x lst)
  match lst
    '() x
    (cons a l) (f a (foldr f x l))

define reverse
  foldl cons empty

;; foldr, as defined above, is a recursive process (see SICP).
;;
;; To make it a linear process, allowing tail call elimination,
;; we could instead (at the cost of an extra pass over lst):
;;
;define foldr(f x lst)
;  foldl f x (reverse lst)

define append(a b)
  foldr cons b a

define append*(. lsts)  ; a lispy append should allow varargs...
  foldr append empty lsts

define sum
  foldl + 0

define product
  foldl * 1

define map(f)
  foldr (compose cons f) empty

define sum-matrix
  compose sum (map sum)

;; This one is based on pattern matching; no need for auto-currying.
define zip-two(A B)
  match (cons A B)
    (or (cons '() _) (cons _ '()))
      '()
    (cons (cons a as) (cons b bs))
      cons (list a b) (zip-two as bs)

;; This one is based on pattern matching; no need for auto-currying.
define zip(. args)  ; generalized to n inputs
  match args
    (list-no-order '() _ ...)  ; at least one input empty
      '()
    (list (cons xs xss) ...)
      cons (apply list xs) (apply zip xss)

module+ main
  define a '(1 2)
  define b '(3 4)
  define c '(5 6 7)
  define M '((1 2)
             (3 4))
  define f(x) {x * x}
  define double (λ (x) (* 2 x))
  define double-all (map double)
  append a b
  reverse c
  sum a
  product b
  product (append a b)  ; here we need some parentheses to apply the append first.
  append* a b c
  map f c
  double-all c
  sum-matrix M
  zip-two a b
  zip a b c
