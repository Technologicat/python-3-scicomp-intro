#lang sweet-exp racket

;; Some very simple infix expression handlers for sweet-exp; mainly useful as a teaching example.
;;
;; If this is to be done properly, this very basic implementation just scratches the surface;
;; for a much more in-depth discussion, see:
;;
;;   https://sourceforge.net/p/readable/wiki/Precedence/
;;
;; which also explains the reasons why sweet-exp does not define precedence by default.


;; Sweet-exp's reader layer defines {} infix expressions to mean:
;;
;;  {x1 op x2 op ... xn}           --> (op x1 x2 ... xn)
;;  {x1 op1 x2 op2 ... op[n-1] xn} --> (nfx x1 op1 x2 op2 ... op[n-1] xn)
;;
;; This module provides nfx, which is just a regular function.
;;
;; Our assumptions:
;;  An infix expression has an initial operand, followed by any number of operator/next-operand pairs.
;;  All operators must be binary (input arity of 2) and return a scalar (output arity of 1).

provide
  contract-out [nfx (->* () #:rest (and/c odd-length? cdr-consists-of-operator-operand-pairs?) any)]

define odd-length?(L)
  odd? length(L)

;; TODO: figure out a better check for value-ness than not(procedure?()).
;; (Generally, the operands are not necessarily numbers, so no number?();
;;  they could be e.g. symbolic.)
;;
define cdr-consists-of-operator-operand-pairs?(L)
  define check-item-pairs(lst)
    cond [empty?(lst) #t]
         [{procedure?(car(lst)) and not(procedure?(cadr(lst)))} check-item-pairs(cddr(lst))]
         [else #f]
  check-item-pairs(cdr(L))


;; a) Left-to-right reduction, no precedence.

;; E.g. {2 + 3 * 4} --> ((2 + 3) * 4)

;;define/contract nfx(. args)
;;  (nfx (->* () #:rest (and/c odd-length? cdr-consists-of-operator-operand-pairs?) any))
define nfx1(. args)
  define infix-process(a lst)
    cond [empty?(lst) a]
         [else
           define(op car(lst))
           define(b cadr(lst))
           infix-process((op a b) cddr(lst))]
  infix-process(car(args) cdr(args))


;; b) Reduction with precedence ordering.

;; In general, this is not a sensible algorithm, as the input is scanned k times,
;; where k is the number of precedence groups. Hence performance is O(k n), where n is the length
;; of the input. Building a tree would probably give better performance for long expressions.

;; List of all operators for nfx2 to recognize. As symbols, in decreasing order of precedence.
;; Each operator must accept two arguments, and return a single value.
;;
;; Each operator in the same group (sublist) has the same precedence.
;;
;; These are basically names of Racket procedures.
;;
define sym-groups '((expt) (* /) (+ -))
;define sym-groups '((expt) (*) (/) (+ -))  ; e.g. Landau & Lifshitz: * binds more tightly than /

;define ** expt  ; (Fortran and Python users could do this, but "expt" is standard in Racket.)

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
        error(format("infix expr ~a: non-singleton result ~a; maybe unknown op?" args result))]
  car(result)

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
           cond( [member(op target-ops) infix-process((op a b) rest out)]  ; "a op b" --> result
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
  ;; Can also call functions in the expressions. This works, because the function call is evaluated
  ;; before its value is passed into nfx.
  {1 + 2 * log(5)}
  {2 * log(5) + 1}
