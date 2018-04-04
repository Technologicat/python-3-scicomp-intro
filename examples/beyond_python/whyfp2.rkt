#lang sweet-exp "autocurry2.rkt"

define foldl(f x lst)
  match lst
    '() x
    (cons a l) (foldl f (f a x) l)

define foldr(f x lst)
  match lst
    '() x
    (cons a l) (f a (foldr f x l))

;define foldr(f x lst)
;  foldl f x (reverse lst)

define append(a b)
  foldr cons b a

define reverse
  foldl cons empty

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
  map f c
