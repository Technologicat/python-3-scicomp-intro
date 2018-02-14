#lang sweet-exp racket

;;; Sieve of Eratosthenes using Racket's generators.
;;;
;;; Rackety stream approach. Try cutting candidates.

require racket/generator

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

;; Yield only candidates passing a superficial inspection.
;;
;; In base-10, we know that primes larger than 10 must end in 1, 3, 7 or 9.
;;
;; However, actually slower than just in-naturals(2). This is because of the stream layer.
define candidates()
  generator ()
    yield 2
    yield 3
    yield 5
    yield 7
    for ([x in-naturals(1)])
      define b {x * 10}
      yield {b + 1}
      yield {b + 3}
      yield {b + 7}
      yield {b + 9}

define sieve()
  generator ()
    let loop ([s sequence->stream(in-producer(candidates()))])
      define m (stream-first s)
      yield m  ; invariant: the first element of s is prime
      loop
        stream-filter
          λ　(x)
            not (divisible x m)
          stream-rest s

module+ main
  define main()
    for/list ([p in-producer(sieve())]
              [k in-range(1000)])
      p
  time main()
