#lang sweet-exp racket

;;; Sieve of Eratosthenes using infinite streams, custom implementation (see stream.rkt).
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
    naturals-from
      λ (n)
        scons n (sadd ones (naturals-from n))
    sieve
      λ (s)
        scons
          scar s  ; invariant: the first element of s is prime
          sieve
            sfilter
              λ (x)
                not (divisible x (scar s))
              scdr s
    primes
      sieve (naturals-from 2)
  ;
  define lst (s->list primes #:nterms 100)
  displayln lst
  ;
  displayln (sref primes 200)  ; find the 200th prime
