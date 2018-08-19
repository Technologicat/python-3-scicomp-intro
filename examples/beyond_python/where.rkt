#lang sweet-exp racket

;; Experiment at a Haskell-style "where". Due to Racket's prefix syntax,
;; the form itself must have some other name.
;;
;; We choose the names let0, let*0, letrec0, in analogy with begin0.

require syntax/parse/define

provide let0 let*0 letrec0 where

define-syntax where(stx) (raise-syntax-error 'where "only meaningful inside let0" stx)

;; The "where" is arguably syntactic saccharine, but OTOH it improves readability.
;;
;; We place the "where" inside the bindings block to make this look sweeter in sweet-exp;
;; now let0 doesn't need to use GROUP "\\" to declare the bindings.
;;
require (for-meta 2 racket/base)
require (for-syntax syntax/parse/define)
begin-for-syntax
  define-syntax-parser make-where-form  ; phase 2
    [_ the-let-stx] #:with ooo (quote-syntax ...)  ; let the inner parser see a "..."
      syntax
        syntax-parser
          #:literals (where)
          [_ body ooo (where (k v) ooo)]
            syntax
              the-let-stx
                ((k v) ooo)
                body
                ooo

define-syntax let0 (make-where-form let)
define-syntax let*0 (make-where-form let*)
define-syntax letrec0 (make-where-form letrec)

module+ main
  let0
    displayln x
    where
      (x 42)
  ;
  let*0
    displayln a
    displayln b
    where
      (a 1)
      (b {a + 1})
  ;
  define ≠(. args)
    not (apply = args)
  letrec0
    even? 42
    where
      even?
        λ (n)
          {{n = 0} or (odd? {n - 1})}
      odd?
        λ (n)
          {{n ≠ 0} and (even? {n - 1})}
