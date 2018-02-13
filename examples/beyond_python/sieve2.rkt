#lang sweet-exp racket

;;; Sieve of Eratosthenes using infinite streams, custom implementation (see stream.rkt).
;;;
;;; This is a classical Lisp approach to the problem.
;;;
;;; See SICP 2nd ed., sec. 3.5.1.
;;;   https://mitpress.mit.edu/sicp/full-text/book/book-Z-H-24.html#%_sec_3.5.1

require (only-in "stream.rkt" scons scar scdr sref sfilter sadd s->list)

define divisible(n k)
  {(remainder n k) = 0}

letrec
  \\
    ones
      scons 1 ones
    naturals-from  ; needs to obey the custom stream interface, hence Racket's "in-naturals" won't do.
      λ (n)  ; letrec has no "implicit lambda" for functions, unlike define, so do it manually.
        scons n (sadd ones (naturals-from n))
    sieve
      λ (s)
        define m (scar s)
        scons
          m       ; invariant: the first element of s is prime (so output it)
          sieve   ; in the tail, we store the procedure to compute the rest of the stream
            sfilter
              λ (x)
                not (divisible x m)
              scdr s
    primes
      sieve (naturals-from 2)
  ;
  define lst (s->list primes #:nterms 100)
  displayln lst
  ;
  ;; As Abelson and Sussman point out in SICP, the beauty of the stream abstraction
  ;; is that we can find the nth prime by just indexing into the stream:
  displayln (sref primes 200)
