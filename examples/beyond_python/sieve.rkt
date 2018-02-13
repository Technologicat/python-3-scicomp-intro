#lang sweet-exp racket

;;; Sieve of Eratosthenes using Racket's generators, packaged into infinite streams,
;;; using streams from Racket's standard library.
;;;
;;; A generator can be packaged into a sequence (using "in-producer"), which can be
;;; further packaged into a stream, which then supports "stream-first" and "stream-rest".
;;;
;;; See the documentation:
;;;   https://docs.racket-lang.org/reference/Generators.html
;;;   https://docs.racket-lang.org/reference/sequences.html
;;;   https://docs.racket-lang.org/reference/streams.html
;;;
;;; For a version using plain infinite streams, see SICP 2nd ed., sec. 3.5.1.
;;;   https://mitpress.mit.edu/sicp/full-text/book/book-Z-H-24.html#%_sec_3.5.1

require racket/generator

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

define remove-multiples-of(m stream)
  sequence->stream
    in-producer
      generator ()
        let loop ([s stream])
          define k stream-first(s)
          cond
            not(divisible(k m))
              yield k
          loop stream-rest(s)

define sieve()
  sequence->stream
    in-producer
      generator ()
        let loop ([s in-naturals(2)])
          define m stream-first(s)
          yield m  ; invariant: the first element of s is prime
          loop remove-multiples-of(m stream-rest(s))

module+ main
  for/list ([p sieve()]
            [k in-range(100)]) ; step a finite sequence in parallel to eventually stop the generator
    p
