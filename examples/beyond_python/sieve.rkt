#lang sweet-exp racket

;;; Compute prime numbers. Sieve of Eratosthenes using Racket's generators.
;;;
;;; For the best implementation, see sieve7.rkt.
;;;
;;; For an implementation using custom infinite lists, see sieve2.rkt.
;;; For various other implementations, see sieve3.rkt through sieve6.rkt.
;;;
;;; For the original inspiration, see SICP 2nd ed., sec. 3.5.1.
;;;   https://mitpress.mit.edu/sicp/full-text/book/book-Z-H-24.html#%_sec_3.5.1

;;; This is a first direct translation of the Python example into Racket, and as the length of the
;;; program shows, this particular packaging of the idea is definitely more pythonic than rackety!
;;;
;;; In Python, a generator (once invoked) is just an iterable, so the use site sees it as a lazy list.
;;; Not so in Racket, which makes a distinction between generators, sequences and streams:
;;;
;;; - A generator, once invoked, is basically a procedure; calling it returns the next value.
;;;
;;;   This works just like in Python: recall that invoking a Python generator returns an iterator,
;;;   and you extract values from the generator by calling next() on this iterator.
;;;
;;;   Racket however makes the distinction that strictly speaking, it makes no sense to iterate
;;;   over /a procedure/. To iterate over the values the generator yields, we use "in-producer"
;;;   to tell Racket to package the generator into a sequence first.
;;;
;;; - A sequence is an abstract data type for an ordered collection of values; one can "for" over it.
;;;
;;; - A stream is a subtype of sequence that understands the concepts of "first" and "rest",
;;;   needed in the classic list processing paradigm (process first element, loop over the rest).

;;; Relevant parts of Racket documentation.
;;;
;;;   Gentle introduction to sequences:
;;;     https://docs.racket-lang.org/guide/for.html#%28part._sequences%29
;;;
;;;   API reference:
;;;     https://docs.racket-lang.org/reference/Generators.html
;;;     https://docs.racket-lang.org/reference/sequences.html
;;;     https://docs.racket-lang.org/reference/streams.html

require racket/generator

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

;; Just like in the Python example, we define two generators that produce streams.

;; Take a stream, and return a stream with multiples of m filtered out.
define remove-multiples-of(m stream)
  ;; Three levels of wrappers? The complexity here hints that we are likely missing something;
  ;; surely there must be a more rackety way of doing this! (See sieve3.rkt for the solution.)
  sequence->stream   ; Package as a stream the...
    in-producer      ; ...sequence that encapsulates the...
      generator ()   ; ...generator, which is defined as:
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
