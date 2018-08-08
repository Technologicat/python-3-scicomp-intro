#lang sweet-exp racket

;; alambda: capture and export a "self", using letrec.
;;
;; Allows recursion in an unnamed function.
;;
;; Inspired by Doug Hoyte's Let Over Lambda: 50 Years of Lisp.
;; Racketified.

require syntax/parse/define
require "abbrev.rkt"

provide alambda λ/anaphoric self

define-syntax self(stx) raise-syntax-error('self "only meaningful inside alambda" stx)

;; Other than the magic "self", works just like λ.
define-syntax-parser alambda
  [this-stx argspec body ...]
    with-syntax ([self (datum->syntax #'this-stx 'self)])  ; break hygiene
      syntax
        letrec
          \\
            self (λ argspec body ...)
          self

abbrev alambda λ/anaphoric

module+ main
  map
    λ/anaphoric (n [acc 1])  ; no name!
      cond
        {n = 0}
          acc
        else
          self {n - 1} {n * acc}  ; but it can call itself.
    (range 10)  ; same as (build-list 10 values)
