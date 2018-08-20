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

;; This version optimizes e.g. {a + b + c} --> (+ a b c) inside the expressions.

;; Our clients will have "nfx" available at phase 0 (the plain-old run time phase).
;;
;;   https://beautifulracket.com/explainer/importing-and-exporting.html#phases
;;
;; Note that the DrRacket macro stepper will not expand the invocations of nfx in this module
;; (unless macro hiding is disabled), but will expand them in any modules that require this one.
;
provide nfx

;; TODO: improve messages for syntax errors; currently the "at:" and "in:" are the same
;; TODO: because #:fail-unless does not allow specifying them manually (unlike raise-syntax-error).
;;
require syntax/parse/define
require
  for-syntax
    syntax/parse
    racket/match
    only-in racket/list empty empty?
    only-in racket/function curry

;; Each arg can be any s-expr, so we don't do any checking on that.
;; We just check that stx has identifiers in even-numbered positions (starting from 0).
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
define-syntax-parser nfx
  (_ x0:expr)
    #'x0
  (_ x0:expr (~and (~seq (~seq op:id x:expr) ...+)  ; The ~and pattern checks each term is a pair,
                   (~seq id-expr-pair ...+)))       ; while also binding a name to the whole pair.
    ;infix-to-prefix-left-to-right(#'(x0 id-expr-pair ...))  ; choose either implementation here
    infix-to-prefix-with-precedence(#'(x0 id-expr-pair ...))

;; a) Left-to-right, no precedence.

;; E.g. {2 + 3 * 4} --> ((2 + 3) * 4)
;;      {2 + 3 + 4 * 5} --> (* (+ 2 3 4) 5)
begin-for-syntax
  define infix-to-prefix-left-to-right(stx)
    define loop(prev-op acc stxs)
      match stxs
        '()
          reverse acc  ; final commit
        (list-rest op x rest)
          let ([op-sym (syntax->datum op)])  ; check the symbol only, ignoring what it's bound to
            loop
              op-sym
              cond
                (eq? prev-op 'none)     ; init
                  list(x acc op)
                (eq? op-sym prev-op)    ; same op-sym - buffer and continue
                  cons x acc
                else                    ; different op-sym - commit and reset
                  list(x (reverse acc) op)
              rest
    ;; syntax->list retains the lexical context (variable bindings etc.) at any inner levels
    define result
      match (syntax->list stx)
        (cons x0 terms)
          loop 'none x0 terms
    datum->syntax stx result

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
  define sym-groups '((expt ^ **) (* /) (+ -) (and) (or))
  ; e.g. Landau & Lifshitz: * binds more tightly than /, so that {1 / 2 * pi} means {1 / {2 * pi}}
  ;define sym-groups '((expt ^ **) (*) (/) (+ -) (and) (or))

begin-for-syntax
  define infix-to-prefix-with-precedence(stx)
    define result
      for/fold
        ([acc (syntax->list stx)])
        ([grp sym-groups])
        reduce-given-ops grp acc
    match result
      (cons y '())  ; the result should be a one-element list (containing nested lists)
        datum->syntax stx y
      (cons y ys)
        raise-syntax-error 'nfx format("failed with extra terms ~a" ys) stx

;; Reduce on given operators (symbols) only, pass the rest of L through as-is.
;; Here L is an infix expression represented as a list.
begin-for-syntax
  define reduce-given-ops(op-syms stx-list)
    define reverse-if-pair(x) (cond [(pair? x) (reverse x)] [else x])
    define loop(prev-op acc stxs out)  ; here prev-op tracks only ops in target-ops
      match stxs
        '()
          reverse (cons (reverse-if-pair acc) out)  ; final commit
        (list-rest op x rest)
          let ([op-sym (syntax->datum op)])  ; check the symbol only, ignoring what it's bound to
            cond
              (eq? prev-op 'none)
                cond
                  (member op-sym op-syms)
                    loop op-sym list(x acc op) rest out  ; init
                  else  ; not ours; copy out
                    ;; commit a and op to out; b becomes new a (single item!)
                    loop 'none x rest (foldl cons out list(acc op))
              ;; prev-op not 'none
              {(eq? op-sym prev-op) and (member op-sym op-syms)}
                loop op-sym (cons x acc) rest out  ; same op-sym (and ours) - buffer and continue
              ;; prev-op not 'none; and op-sym either different from it, or not ours.
              else  ; reset prev-op, commit acc, and redo this step
                loop 'none (reverse acc) stxs out
    ;; If expr has only one subexpr, do nothing; this catches cases like {x * y expt z},
    ;; where a <- (* x (expt y z)), and lst is empty, right at the start when we are called for (+ -).
    ;;
    ;; loop() would reverse the only subexpr, because we construct everything else with the help of
    ;; cons and reverse. In all other cases, whenever loop() hits reverse(), "a" is a
    ;; *list of subexpressions*.
    match stx-list
      (cons x0 '())
        stx-list
      (cons x0 terms)
        loop 'none x0 terms empty

module+ main
  ;(nfx 2 * 3 * 5)  ; sweet-exp handles this case by default, so we call nfx manually to test it
  {2 * 3 + 4}    ; both: (2 * 3) + 4 = 10
  {2 + 3 * 4}    ; left to right:   (2 + 3) * 4 = 20
                 ; with precedence: 2 + (3 * 4) = 14
  {5 * 2 expt 5} ; left to right:   (5 * 2) expt 5 = 10⁵
                 ; with precedence: 5 * (2 expt 5) = 160
  ;; Can also call functions in the expressions.
  {1 + 2 * log(5)}
  {2 * log(5) + 1}
  {#t or #f and #t}
