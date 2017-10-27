#lang sweet-exp racket

;; A simple left-to-right infix handler for sweet-exp.
;;
;; An infix expression has an initial operand, followed by any number of operator/next-operand pairs.
;;
provide
  contract-out [nfx (->* () #:rest (and/c odd-length? cdr-consists-of-operator-operand-pairs?) any)]

define odd-length?(L)
  odd? length(L)

define cdr-consists-of-operator-operand-pairs?(L)
  define check-item-pairs(lst)
    cond [empty?(lst) #t]
         [procedure?(car(lst)) check-item-pairs(cddr(lst))]
         [else #f]
  check-item-pairs(cdr(L))

;;define/contract nfx(. args)
;;  (nfx (->* () #:rest (and/c odd-length? cdr-consists-of-operator-operand-pairs?) any))
define nfx(. args)
  define infix-process(a lst)
    cond [empty?(lst) a]
         [else
           define(op car(lst))
           define(b cadr(lst))
           infix-process((op a b) cddr(lst))]
  infix-process(car(args) cdr(args))
  
module+ main
  {2 + 3 * 4}  ; (2 + 3) * 4
  {2 * 3 + 4}  ; (2 * 3) + 4
