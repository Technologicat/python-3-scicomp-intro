#lang sweet-exp racket

;;; Sieve of Eratosthenes using Racket's generators.
;;;
;;; This implementation uses just generators and procedures.

require racket/generator

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

define sieve()
  generator ()
    let loop ([m 2]
              [check (λ (x) x)])
      cond
        check(m)
          yield m
      loop
        {m + 1}
        compose
          λ　(x)  ; filter out multiples of m
            cond
              (eq? x #f)  ; if already suppressed, pass-through the #f
                #f
              (not (divisible x m))
                x
              else
                #f  ; not prime, suppress
          check

module+ main
  define main()
    for/list ([p in-producer(sieve())]
              [k in-range(1000)])
      p
  time main()  ; performance test, https://docs.racket-lang.org/reference/time.html
