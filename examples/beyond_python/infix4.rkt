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
;; This module provides nfx as a macro.
;;
;; Our assumptions:
;;  An infix expression has an initial operand, followed by any number of operator/next-operand pairs.
;;  All operators must be binary (input arity of 2) and return a scalar (output arity of 1).

;; Implementations with simple left-to-right application and precedence processing are provided.
;; The version with precedence processing currently recognizes (expt * / + -); see sym-groups below.

;; Our clients will have "nfx" available at phase 0 (the plain-old run time phase).
;;
;;   https://beautifulracket.com/explainer/importing-and-exporting.html#phases
;;
;; Note that the DrRacket macro stepper will not expand the invocations of nfx in this module
;; (unless macro hiding is disabled), but will expand them in any modules that require this one.
;
provide nfx

;; TODO: optimize {a + b + c} --> (+ a b c); need to look up the next operator, build the output
;; TODO: into a temporary and commit only when the next operator is different or at end of input.

;; TODO: improve messages for syntax errors; currently the "at:" and "in:" are the same
;; TODO: because #:fail-unless does not allow specifying them manually (unlike raise-syntax-error).
;;
require (for-syntax syntax/parse)
define-syntax (nfx stx)
  syntax-parse stx
    [(_ x0:expr) #'x0]
    [(_ x0:expr op:id x:expr ...)
     #:fail-unless odd-length?(#'(x0 op x ...))
                   "last operand missing, expected x0 [op x] ..."
     #:fail-unless op-arg-pairs?(#'(op x ...))
                   "non-identifier in operator position, expected x0 [op x] ..."
     ;infix-to-prefix-left-to-right(#'(x0 op x ...))]  ; choose either implementation here
     infix-to-prefix-with-precedence(#'(x0 op x ...))]

;; Each arg can be any s-expr, so we don't do any checking on that.
;; We just check that, when converted a list, stx has identifiers
;; in positions 0, 2, 4, ...
;;
;; Why identifiers? An s-expr such as (if (x < 0) (-) (+)) is a valid operator in Racket,
;; but the nfx variant with precedence cannot work with arbitrary s-expr operators,
;; because in general, the precedence of the result then depends on the data at run time,
;; whereas macro expansion occurs at compile time.
;;
;; Thus, we take the easy way out and require that each operator is an identifier.
;;
;; The nfx variant with precedence then further checks that it knows about all the operators
;; used in the expression, and raises a syntax error if the result did not reduce due to
;; unknown operators being present.
;;
require (for-syntax (only-in racket/list empty? empty))
begin-for-syntax
  define op-arg-pairs?(stx)
    ;; we don't need any lexical context here, so syntax->datum on the whole input is fine
    define L syntax->datum(stx)
    define op cond( [{length(L) > 0} datum->syntax(stx car(L))]
                    [else datum->syntax(stx empty)] )
    define rest cond( [{length(L) > 2} datum->syntax(stx cddr(L))]
                      [else datum->syntax(stx empty)] )
    cond [empty?(L) #t]
         [identifier?(op) op-arg-pairs?(rest)]
         [else #f]

begin-for-syntax
  define odd-length?(stx)
    ;; we don't need any lexical context here, so syntax->datum on the whole input is fine
    odd? length(syntax->datum(stx))


;; a) Left-to-right, no precedence.

;; E.g. {2 + 3 * 4} --> ((2 + 3) * 4)

;; We extract the source code from the given syntax object, process it,
;; and finally insert back the context information (lexical scope etc.)
;; from the syntax object.
;;
begin-for-syntax
  define infix-to-prefix-left-to-right(stx)
    define iter(a lst)
      cond [empty?(lst) a]
           [else
             define(op car(lst))
             define(b cadr(lst))
             define(rest cddr(lst))
             iter(`(,op ,a ,b) rest)]
    ;; syntax->list retains the lexical context (variable bindings etc.) at any inner levels
    define L syntax->list(stx)
    datum->syntax(stx iter(car(L) cdr(L)))


;; b) With operations ordered by precedence.

;; The input is scanned k times, where k is the number of precedence groups.
;; Hence performance is O(k n), where n is the length of the input.

;; List of all operator symbols for nfx to recognize, in decreasing order of precedence.
;; Each operator must accept two arguments, and return a single value.
;;
;; Each operator in the same group (sublist) has the same precedence.
;;
;; These are basically names of Racket procedures, as symbols.
;;
;; Note that in the expression, the operators are free variables; the actual binding
;; for each operator symbol can come from anywhere, and this macro version of nfx
;; doesn't care about that: we only *reorganize symbols at the syntax level*.
;;
begin-for-syntax
  ; standard
  define sym-groups '((expt) (* /) (+ -))
  ; e.g. Landau & Lifshitz: * binds more tightly than /, so that {1 / 2 * pi} means {1 / {2 * pi}}
  ;define sym-groups '((expt) (*) (/) (+ -))

begin-for-syntax
  define infix-to-prefix-with-precedence(stx)
    define L syntax->list(stx)
    define result
      for/fold ([lst L]) ([grp sym-groups])
        reduce-given-ops(grp lst)
    cond [{length(result) > 1}  ; the result should be a one-element list (containing nested lists)
          raise-syntax-error('nfx format("failed with result ~a; maybe unknown op" result) stx)]
    datum->syntax(stx car(result))

;; Reduce on given operators (symbols) only, pass the rest of L through as-is.
;; Here L is an infix expression represented as a list.
;;
begin-for-syntax
  define reduce-given-ops(target-ops L)
    define iter(a lst out)
      cond [empty?(lst) reverse(cons(a out))]  ; last remaining atom
           [else  ; here lst is always guaranteed to have op and b
             define(op car(lst))
             define(op-sym syntax->datum(op))  ; we need just the symbol for precedence checking
             define(b cadr(lst))
             define(rest cddr(lst))  ; the tail may be empty
             cond( [member(op-sym target-ops) iter(`(,op ,a ,b) rest out)]  ; "a op b" --> result
                   [else
                      define(new-out foldl(cons out `(,a ,op)))  ; append "a op" to output list
                      iter(b rest new-out)])]                    ; "b" --> new "a"
    iter(car(L) cdr(L) empty)


module+ main
  {2 * 3 + 4}    ; both: (2 * 3) + 4 = 10
  {2 + 3 * 4}    ; left to right:   (2 + 3) * 4 = 20
                 ; with precedence: 2 + (3 * 4) = 14
  {5 * 2 expt 5} ; left to right:   (5 * 2) expt 5 = 10⁵
                 ; with precedence: 5 * (2 expt 5) = 160
  ;; Can also call functions in the expressions.
  {1 + 2 * log(5)}
  {2 * log(5) + 1}
