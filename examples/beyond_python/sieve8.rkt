#lang sweet-exp racket

;;; Sieve of Eratosthenes using Racket's generators.
;;;
;;; Working in base-210 (* 2 3 5 7) in the superficial filter is a more efficient way to
;;; use the idea in sieve7.rkt, improving the ratio of integers remaining to be sieved
;;; by the second stage from 40% to 23%, but no algorithmic improvement.

;; Consider a radix  r = prod(fk),  where fk are the prime factors of r.
;;
;; For any n > r, let
;;
;;  a := (quotient n r)
;;  b := (remainder n r)
;;
;; Then
;;
;;   n = (a * r) + b
;;
;; The first term is obviously divisible by each of the fk, so a necessary (but not sufficient)
;; condition for n to be a prime is that b is not divisible by any of the fk.
;;
;; For example, if r = 10, this produces the familiar observation that any number for which
;; b (the last digit in base-10) is a multiple of 2 or 5 (the factors of 10) cannot be prime.
;; Hence the only possible last digits of a prime, expressed in base-10, are 1, 3, 7, 9.
;;
;; In general: from the range 2, 3, ..., r-1, take out the multiples of each of the fk individually;
;; what remains are the candidate "last digits" (in base r) that a prime number  n > r  may have.
;;
;; This does **not** produce a complete list of primes smaller than r, because there may be primes
;; that are not in fk.
;;
;; Hence, the range 2, 3, ..., r-1 must be checked using other methods, and even for n > r this
;; gives just a preliminary check.
;;
;; For n < r, in this program, we have just taken the output of sieve7.rkt to list the primes
;; up to r = 210. This is more efficient than in-range(2 r), since it creates fewer filters
;; near the start of the chain when these candidates are passed to the actual sieve.

;;; The next stage in performance improvement would be to chain these sieves; compute up to some
;;; number of primes using a sieve with a small radix, then use the result to bootstrap the next
;;; sieve in the chain...

require racket/generator

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

define multiples-of(k #:start [start 0] #:end [end #f])
  generator ()
    let loop ([m start])
      yield m
      cond
        {(not end) or {{m + k} < end}}
          loop {m + k}
        else
          'done

;; for numbers > radix, as explained above.
;;
;; radix itself is composite, since to be useful we use more than one factor.
;;
define candidate-last-digits(factors-of-radix)
  define radix (apply * factors-of-radix)
  define ruled-out  ; rule out last digits b where b is divisible by any of the fk
    list->set
      apply append
        for/list ([f factors-of-radix])
          for/list ([k in-producer(multiples-of(f #:end radix) 'done)])
            k
  define all-last-digits
    for/set ([k in-range(1 radix)])
      k
  ;
  define n-all (set-count all-last-digits)
  define n-ruled-out (set-count ruled-out)
  define ratio (truncate {100 * {n-ruled-out / n-all}})
  displayln
    format("Ruled out ~a of ~a last digits (~a% remaining) using base-~a"
           n-ruled-out n-all {100 - ratio} radix)
  ;
  sort
    set->list
      set-subtract all-last-digits ruled-out
    <

define candidates()
  define factors-of-radix '(2 3 5 7)
  define radix (apply * factors-of-radix)  ; 210
  define primes-up-to-radix '(2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
                              101 103 107 109 113 127 131 137 139 149 151 157 163 167 173 179 181 191
                              193 197 199)  ; get this using sieve7.rkt
  define last-digits candidate-last-digits(factors-of-radix)
  generator ()
    for ([m primes-up-to-radix])  ; could just in-range(2 radix), but more efficient (fewer filters)
      yield m
    let loop ([a radix])
      for ([b last-digits])
        yield {a + b}
      loop {a + radix}

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
