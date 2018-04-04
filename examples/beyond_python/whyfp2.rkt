#lang sweet-exp "autocurry2.rkt"

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

module+ main
  define a '(1 2)
  define b '(3 4)
  define c '(1 2 3)
  define f(x) {x * x}
  append a b
  reverse c
  sum a
  product b
  product (append a b)  ; here we need some parentheses to apply the append first.
  append* a b c
  map f c
