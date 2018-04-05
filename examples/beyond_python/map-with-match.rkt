#lang sweet-exp racket

;; How to implement pythonic map and zip
;; that terminate on the shortest input.
;;
;; This version demonstrates pattern matching
;; (which is kind of cheating in this exercise,
;;  but a common tool in FP); see racket/match.

;; Map f to multiple lists. For the kth output element,
;; the args of f are the kth item from each input list.
;;
define map(f . lsts)
  let loop ([acc empty]
            [lsts lsts])
    match lsts
      (app (curry apply any empty?) #t)
        reverse acc
      (list (cons x xs) ...)
        loop
          cons
            apply f x
            acc
          xs

;; Mapping by the list() function gives us zip().
define zip (curry map list)

;define zip(. lsts)  ; also a possible definition
;  apply map list lsts

;; Low-level functions

define foldl(f x0 lst)
  match lst
    '()
      x0
    (cons x xs)
      foldl f (f x x0) xs

define reverse (curry foldl cons empty)

;; Map f to one list.
define map1(f lst)
  let loop ([acc empty]
            [lst lst])
    match lst
      '()
        reverse acc
      (cons x xs)
        loop
          cons
            f x
            acc
          xs

define any(pred . lst)
  let loop ([acc lst])
    match acc
      '()
        #f
      (cons x xs)
        cond
          (pred x)
            #t
          else
            loop xs

define all(pred . lst)  ; unused; for completeness
  let loop ([acc lst])
    match acc
      '()
        #t
      (cons x xs)
        cond
          (not (pred x))
            #f
          else
            loop xs

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
