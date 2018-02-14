#lang sweet-exp racket

;;; Sieve of Eratosthenes using Racket's generators.
;;;
;;; Make more efficient by breaking out (skipping the rest of the evalution, like the Nothing monad)
;;; once it is known that the given number cannot be prime.

require racket/generator

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

define sieve()
  generator ()
    define break (make-parameter (void))  ; "break" is a lexically scoped name...
    let loop ([m 2]
              [check (λ (x) x)])
      let/ec ec
        parameterize ([break ec])  ; ...which is here dynamically bound to the current escape cont.
          check m  ; if not prime, this breaks out of the let/ec block
          yield m
      loop
        {m + 1}
        compose
          λ　(x)  ; filter out multiples of m
            cond
              (not (divisible x m))
                x
              else
                (break)()  ; calling a parameter gets its value (here a function, which we then call)
          check

module+ main
  define main()
    for/list ([p in-producer(sieve())]
              [k in-range(1000)])
      p
  time main()
