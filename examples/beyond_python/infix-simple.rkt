#lang sweet-exp racket

;; A very simple infix expression handler for sweet-exp; mainly useful as a teaching example.
;;
;; If this is to be done properly, this very basic implementation just scratches the surface;
;; for a much more in-depth discussion, see:
;;
;;   https://sourceforge.net/p/readable/wiki/Precedence/

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
;;
;; Left-to-right, no precedence.
;;
;; E.g. {2 + 3 * 4} --> ((2 + 3) * 4)
;;      {2 + 3 + 4 * 5} --> (* (+ 2 3 4) 5)
;;
;;
;; This version optimizes e.g. {a + b + c} --> (+ a b c) inside the expressions.
;;
;; Our clients will have "nfx" available at phase 0 (the plain-old run time phase).
;;
;;   https://beautifulracket.com/explainer/importing-and-exporting.html#phases
;;
;; Note that the DrRacket macro stepper will not expand the invocations of nfx in this module
;; (unless macro hiding is disabled), but will expand them in any modules that require this one.
;
provide nfx

require syntax/parse/define
require (for-syntax racket/list racket/match)

define-syntax-parser nfx
  (_ x0:expr)
    #'x0
  (_ x0:expr (~and (~seq (~seq op:id x:expr) ...+)  ; The ~and pattern checks each term is a pair,
                   (~seq id-expr-pair ...+)))       ; while also binding a name to the whole pair.
    infix-to-prefix #'(x0 id-expr-pair ...)

begin-for-syntax
  define infix-to-prefix(stx)
    define loop(prev-op a lst out)
      match lst
        '()
          reverse (cons (reverse a) out)  ; final commit
        (list-rest op b rest)
          let ([op-sym (syntax->datum op)])  ; check the symbol only, ignoring what it's bound to
            ;; at init, we use "a" to pass in the first operand; everywhere else, "a" is a list
            cond
              (eq? prev-op 'none)     ; init
                loop op-sym list(b a op) rest out
              (eq? op-sym prev-op)    ; same op-sym - buffer and continue
                loop op-sym (cons b a) rest out
              else                    ; different op-sym - commit and reset
                loop op-sym list(b (reverse a) op) rest out
    ;; syntax->list retains the lexical context (variable bindings etc.) at any inner levels
    match (syntax->list stx)
      (cons x xs)
        match (loop 'none x xs empty)
          (cons y '())  ; the result should be a one-element list (containing nested lists)
            datum->syntax stx y
          (cons y ys)
            raise-syntax-error 'nfx format("failed with extra terms ~a" ys) stx

module+ main
  (nfx 2 * 3 * 5)    ; sweet-exp handles this case by default, so we call nfx manually to test it.
  (nfx 1 / 2 / 3)
  {2 * 3 + 4}        ; (2 * 3) + 4 = 10
  {2 + 3 * 4}        ; (2 + 3) * 4 = 20
  {2 + {3 * 4}}      ; 2 + (3 * 4) = 14 - use explicit braces to demand specific precedence.
  {5 * 2 expt 5}     ; (5 * 2) expt 5 = 10⁵
  {1 + 2 * log(5)}   ; can also call functions.
  {2 * log(5) + 1}
  {#t or #f and #t}  ; (#t or #f) and #t - works also for logical expressions.
