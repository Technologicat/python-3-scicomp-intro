#lang sweet-exp racket

;;; Sieve of Eratosthenes using Racket's generators.
;;;
;;; Final performance improvement: check only reasonable candidates.
;;; This gives the first 5000 primes in ~5 seconds on an i7.

require racket/generator

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

;; Yield only candidates passing a superficial inspection.
;;
;; In base-10, we know that primes larger than 10 must end in 1, 3, 7 or 9.
;; In other words, we pre-sieve by the factors of the radix, here 2 and 5.
;;
define candidates()
  generator ()
    yield 2
    yield 3
    yield 5
    yield 7
    let loop ([x 10])
      yield {x + 1}
      yield {x + 3}
      yield {x + 7}
      yield {x + 9}
      loop {x + 10}

define sieve()
  generator ()
    define s candidates()
    define break (make-parameter (void))
    let loop ([m s()]
              [check (λ (x) x)])
      let/ec ec
        parameterize ([break ec])
          check m  ; if not prime, this breaks out of the let/ec block
          yield m
      loop
        s()
        compose
          λ　(x)  ; filter out multiples of m
            cond
              (not (divisible x m))
                x
              else
                (break)()
          check

module+ main
  define main()
    for/list ([p in-producer(sieve())]
              [k in-range(1000)])
      p
  time main()
