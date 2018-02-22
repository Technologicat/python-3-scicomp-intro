#lang sweet-exp typed/racket

;; https://docs.racket-lang.org/ts-guide/types.html
;; https://docs.racket-lang.org/ts-reference/special-forms.html

define-type Fold-Procedure(A X)
  ->* (A X) X  ; elt acc
;;
;; Same as:
;;
;define-type FoldProc
;  ∀ (A X)
;    ->* (A X) X

define-type Fold-Applier(A X)
  ->*
    \\
      Fold-Procedure A X ; f
      X                  ; x
      Listof A           ; lst
    X

: foldl Fold-Applier
define foldl(f x lst)
  let loop ([acc x]
            [l lst])
    match l
      '() acc
      (cons a k) (loop (f a acc) k)

: foldr Fold-Applier
define foldr(f x lst)
  match lst
    '() x
    (cons a l) (f a (foldr f x l))

;: tmp
;  ∀ (A)
;    Fold-Procedure(A Listof(A))
;define tmp(a b)
;  cons a b

module+ main
  define lst '(1 2 3 4 5)
  foldl + 0 lst
  foldr * 1 lst
  foldl (inst cons Number Listof(Number)) empty lst
