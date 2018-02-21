#lang sweet-exp racket

;; pi approximation with Euler series acceleration
;;
;; See SICP, 2nd ed., sec. 3.5.3.
;;
;; This implementation originally by Jim Hoover, from:
;; https://sites.ualberta.ca/~jhoover/325/CourseNotes/section/Streams.htm

require "stream.rkt"

; apply an operation (op v e) to each element e of the stream
define op-on-stream(op v s)
  smap
    λ (e)
      op v e
    s

define square(x)
  {x * x}

define partial-sums(s)
  cond
    sempty?(s)
      sempty
    else
      scons
        scar s
        op-on-stream + (scar s) (partial-sums (scdr s))

define pi-summands(n)
  scons {1.0 / n} (smap - pi-summands{n + 2})

define pi-stream
  smul (partial-sums (pi-summands 1)) 4

;; http://mathworld.wolfram.com/EulerTransform.html
;; https://en.wikipedia.org/wiki/Series_acceleration#Euler%27s_transform
define euler-transform(s)
  let ([s0 (sref s 0)]
       [s1 (sref s 1)]
       [s2 (sref s 2)])
    scons
      {s2 - {square{s2 - s1} / {s0 + {-2 * s1} + s2}}}
      euler-transform (scdr s)

define faster-pi-stream
  euler-transform pi-stream

;; Each row of the tableau is the transform of the previous row.
;; The first row is the original stream.
;;
;; This will generate a stream of streams.
define make-tableau(transform s)
  scons
    s
    make-tableau
      transform
      transform s

;; Get the first element from each row of the tableau.
define accelerated-sequence(transform s)
  smap
    scar
    make-tableau
      transform
      s

;; This will NaN out after some terms, because the denominator
;; in euler-transform becomes numerically zero.
define fastest-pi-stream
  accelerated-sequence euler-transform pi-stream

module+ main
  define n 10
  ;
  displayln "raw"
  for/s displayln pi-stream #:nterms n
  ;
  displayln "Euler accelerated"
  for/s displayln faster-pi-stream #:nterms n
  ;
  displayln "with tableau"  ; n = 10 gives already 14 correct decimals.
  for/s displayln fastest-pi-stream #:nterms n
