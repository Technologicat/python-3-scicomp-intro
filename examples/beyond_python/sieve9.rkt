#lang sweet-exp racket

;; Racket port of the fastest Python approach in sieve.py.

require racket/generator
require data/gvector  ; gvector is Racket's dynamic array, similar to Python's "list".
require racket/performance-hint

define primes()
  define memo (make-gvector #:capacity 128)
  generator ()
    define-inline memo-and-yield(m)
      gvector-add! memo m
      yield m
    memo-and-yield 2
    for ([f in-naturals(1)])
      define n {{2 * f} + 1}
;      define check()
;        sequence-andmap
;          λ (p) (not (divisible n p))
;          in-producer
;            gvector-takewhile
;              λ (p) {{p * p} <= n}
;              memo
;            'done
      define check()
        andmap
          λ (p) (not (divisible n p))
          gvector-takewhile
            λ (p) {{p * p} <= n}
            memo
      cond
        check()
          memo-and-yield n

define divisible(n k)
  {(remainder n k) = 0}  ; n mod k

define-inline gvector-takewhile(pred gv)
  for/list ([x in-gvector(gv)]
            #:break (not (pred x)))
    x

;; Surprisingly, using a generator here is slower than building a list.
;;
;define-inline gvector-takewhile(pred gv)
;    generator ()
;      for ([x in-gvector(gv)]
;           #:break (not (pred x)))
;        yield x
;      yield 'done

module+ main
  define main()
    for/list ([p in-producer(primes())]
              [k in-range(1000)])
      p
  time main()
