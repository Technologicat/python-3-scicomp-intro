#lang sweet-exp racket

;; How to implement pythonic map and zip
;; that terminate on the shortest input.

;; Map f to multiple lists. For the kth output element,
;; the args of f are the kth item from each input list.
;;
define map(f . lsts)
  let loop ([acc empty]
            [lsts lsts])
    cond
      (apply any empty? lsts)
        reverse acc  ; done
      else
        loop
          cons
            apply f (map1 car lsts)
            acc
          map1 cdr lsts

;; Mapping by the list() function gives us zip().
define zip (curry map list)

;define zip(. lsts)  ; also a possible definition
;  apply map list lsts

;; Low-level functions

define foldl(f x lst)
  cond
    (empty? lst)
      x
    else
      foldl f (f (car lst) x) (cdr lst)

define reverse (curry foldl cons empty)

;; Map f to one list.
define map1(f lst)
  let loop ([acc empty]
            [lst lst])
    cond
      (empty? lst)
        reverse acc
      else
        loop
          cons
            f (car lst)
            acc
          cdr lst

define any(pred . lst)
  let loop ([acc lst])
    cond
      (empty? acc)
        #f
      (pred (car acc))
        #t
      else
        loop (cdr acc)

define all(pred . lst)  ; unused; for completeness
  let loop ([acc lst])
    cond
      (empty? acc)
        #t
      (not (pred (car acc)))
        #f
      else
        loop (cdr acc)

;; test it
module+ main
  define a '(1 2 3)
  define b '(4 5 6)
  define c '(7 8 9 10)
  define K
    map
      λ (x y z) {x * y * z}
      a
      b
      c
  K
  ;
  define Z
    zip a b c
  Z
  ;
  apply zip Z  ; zip is its own inverse
