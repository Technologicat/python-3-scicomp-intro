#lang sweet-exp racket

;; convert between multiple-values and list

require for-syntax(syntax/parse only-in(racket/syntax format-id with-syntax*))

provide(list->values values->list
        values-ref
        values-first values-second values-third values-fourth
        values-fifth values-sixth values-seventh values-eighth)

define list->values(lst)
  apply values lst

define thunk-values->list(thunk)
  call-with-values(thunk list)

; macro, to postpone evaluation of expr
define-syntax (values->list stx)
  syntax-parse stx
    [(_ expr) #'thunk-values->list( (λ () expr) )]

;; we could also use promises (delay, force) to do the same:
;define delayed-values->list(promise)
;  call-with-values((λ () (force promise)) list)
;
;define-syntax (values->list2 stx)
;  syntax-parse stx
;    [(_ expr) #'delayed-values->list(delay(expr))]

; macro, to postpone evaluation of v until it is passed to values->list
define-syntax (values-ref stx)
  syntax-parse stx
    [(_ v n) #'list-ref(values->list(v) n)]

;; We want to do this:
;define-syntax (values-first stx)
;  syntax-parse stx
;    [(_ v) #'values-ref(v 0)]
;define-syntax (values-second stx)
;  syntax-parse stx
;    [(_ v) #'values-ref(v 1)]
;; ...
;;
;; so we define a macro-generating macro:
;;  (values-nth fourth) --> (define-syntax (values-fourth ...))

begin-for-syntax
  define m hash(0 'first  1 'second  2 'third    3 'fourth
                4 'fifth  5 'sixth   6 'seventh  7 'eighth)
define-syntax (values-nth original-stx)
  syntax-parse original-stx
    [(_ num)
     (with-syntax* ([s hash-ref(m syntax->datum(#'num))]
                    [macro/id format-id(original-stx "values-~a" #'s)])
         #'(define-syntax (macro/id stx)
             (syntax-parse stx
               [(_ v) #'values-ref(v num)])))]

(values-nth 0)
(values-nth 1)
(values-nth 2)
(values-nth 3)
(values-nth 4)
(values-nth 5)
(values-nth 6)
(values-nth 7)

;; The needlessly complicated way to do this, for just 8 cases, is to use:
;require "macro-for.rkt"
;macro-for ([i in-range(8)])
;  (values-nth i)

;; test it

define tmp()
  values(0 1 2 3 4)

define tmp2(a)
  define lst map((λ (x) (+ x a)) '(0 1 2 3 4))
  list->values(lst)

module+ main
  tmp()
  values->list(tmp())
  tmp2(3)
  values->list(tmp2(3))
  list-ref(values->list(tmp2(3)) 3)  ; extracting a single value
  values-ref(tmp2(3) 3)              ; shorthand macro
  ;; further shorthand macros
  values-first(tmp2(3))
  values-second(tmp2(3))
  values-third(tmp2(3))
  values-fourth(tmp2(3))
  values-fifth(tmp2(3))
  ;; not composable, since it's a macro.
  ;define f (λ (v) values-ref(v 0))
  ;define g compose(displayln f)
  ;g(tmp2(3))  ; doesn't work
