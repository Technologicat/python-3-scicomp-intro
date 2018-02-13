#lang sweet-exp racket

;;; Sieve of Eratosthenes using Racket's generators.
;;;
;;; Rackety approach, also the best performance out of the three. (Python is still a lot faster here.)

require racket/generator

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

define sieve()
  generator ()  ; now only essential complexity (we are making a generator).
    let loop ([s in-naturals(2)])
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
  time main()  ; performance test, https://docs.racket-lang.org/reference/time.html
