#lang sweet-exp racket

;; Towards building a macro.
;;
;; This version still provides nfx as a function, but defers evaluation until the end,
;; so that we get the final expression as a list before any operators are actually applied.
;;
;; The final step is then to use the same approach in a version that operates at the level
;; of syntax and symbols; see infix4.rkt.

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


;; a) Left-to-right reduction, no precedence.

;; E.g. {2 + 3 * 4} --> ((2 + 3) * 4)

define nfx1(. args)
  define infix-process(a lst)
    cond [empty?(lst) a]
         [else
           define(op car(lst))
           define(b cadr(lst))
           define(rest cddr(lst))
           infix-process(`(,op ,a ,b) rest)]
  define expr infix-process(car(args) cdr(args))
  eval expr (make-base-namespace)


;; b) Reduction with precedence ordering.

define sym-groups '((expt) (* /) (+ -))

define make-op-groups(groups)
  for/list ([grp groups])
    syms-to-procedures(grp)

;; https://stackoverflow.com/questions/1045069/how-do-i-apply-a-symbol-as-a-function-in-scheme
define syms-to-procedures(syms)
  define ns (make-base-namespace)
  for/list ([sym syms])
    eval(sym ns)

define op-groups make-op-groups(sym-groups)

define nfx2(. args)
  define result
    for/fold ([lst args]) ([grp op-groups])
      reduce-given-ops(grp lst)
  cond [{length(result) > 1}
        error(format("nfx: in ~a: non-singleton result ~a; maybe unknown op?" args result))]
  define expr car(result)
  eval expr (make-base-namespace)

;; Reduce on given operators (procedures) only, pass the rest of L through as-is.
;; Here L is an infix expression represented as a list.
;;
define reduce-given-ops(target-ops L)
  define infix-process(a lst out)
    cond [empty?(lst) reverse(cons(a out))]  ; last remaining atom
         [else  ; here lst is always guaranteed to have op and b...
           define(op car(lst))
           define(b cadr(lst))
           define(rest cddr(lst))  ; ...but the tail may be empty
           cond( [member(op target-ops) infix-process(`(,op ,a ,b) rest out)]  ; "a op b" --> result
                 [else
                    define(new-out foldl(cons out `(,a ,op)))  ; append "a op" to output list
                    infix-process(b rest new-out)])]           ; "b" --> new "a"
  infix-process(car(L) cdr(L) empty)

;; choose which version to use (and export)
define nfx nfx2

module+ main
  {2 * 3 + 4}    ; both: (2 * 3) + 4 = 10
  {2 + 3 * 4}    ; nfx1: (2 + 3) * 4 = 20, left-to-right
                 ; nfx2: 2 + (3 * 4) = 14, usual math precedence
  {5 * 2 expt 5} ; nfx1: (5 * 2) expt 5 = 10⁵
                 ; nfx2: 5 * (2 expt 5) = 160
  ;; Can also call functions in the expressions.
  {1 + 2 * log(5)}
  {2 * log(5) + 1}
