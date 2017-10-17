#!/usr/bin/env racket
#lang sweet-exp racket

if {1 < 2}
  begin  ; use "begin" to evaluate several exprs in place of one (keeping the result of the last one)
    displayln "foo"
    displayln "bar"
  null   ; Racket's "if" requires an else branch, like Python's expression form of if

;; In Racket, cond is preferred over if.
;;
;; cond has an implicit begin (each branch can have multiple exprs).
;;
cond [{1 < 2} (displayln "foo") (displayln "bar")]

(define get-y     ; not a function definition yet...
    (let ([y 0])
      (lambda ()  ; this makes get-y into a function...
        y)))      ; ...the body of which is here

;; y is not visible here, only get-y is

(get-y)

((lambda (x) (* x x)) 3)
(λ (x) {x * x}) 3

(expt 3 2)  ; exponentiation is denoted expt
