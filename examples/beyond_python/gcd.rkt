#lang sweet-exp typed/racket

;; https://en.wikipedia.org/wiki/Recursion_(computer_science)#Generative_recursion

: gcd (->* (Positive-Integer Nonnegative-Integer) Integer)
define gcd(x y)
  cond
    {y = 0}
      x
    else  ; typed/racket infers that in this branch, y must be Positive-Integer
      gcd y (remainder x y)

module+ main
  gcd 2 3
  gcd 60 24
