#lang racket

(define (foo n)
  '(n 1 2 3))      ; quoting puts a literal symbol 'n into the list

(define (bar n)
  `(,n 1 2 3))     ; quasiquote, unquote to use current value of n

(define (baz n)
  (list n 1 2 3))  ; using a function call (list), n gets evaluated as an argument

(define (qux n)
  (n 1 2 3))       ; function call; this expects n to be a function accepting 3 arguments.

(foo 5)
(bar 5)
(baz 5)
(qux (λ args (apply + args)))  ; passing in a varargs function is OK
(qux 5)                        ; but this crashes, as the constant 5 is not a function

;(define n 1)
;(define a (list n 3))
;(set! n 2)
;(define b (list n 5))
;a
;b
