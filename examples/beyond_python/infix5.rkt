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
  ; The ~and pattern checks each term is a pair, while also binding a name to the whole pair.
  (this-stx x0:expr (~and (~seq (~seq op:id x:expr) ...+)
                          (~seq id-expr-pair ...+)))
    ;infix-to-prefix-left-to-right(#'(x0 id-expr-pair ...))  ; choose either implementation here
    infix-to-prefix-with-precedence(#'(x0 id-expr-pair ...) #'this-stx)

;; a) Left-to-right, no precedence.

;; E.g. {2 + 3 * 4} --> ((2 + 3) * 4)
;;      {2 + 3 + 4 * 5} --> (* (+ 2 3 4) 5)
begin-for-syntax
  define infix-to-prefix-left-to-right(stx)
    ;; Only the initial acc is a single term; after the first init, it is always a list.
    define loop(prev-op acc stxs-in)
      match stxs-in
        '()
          reverse acc  ; final commit
        (list-rest op x rest-in)
          let ([op-sym (syntax->datum op)])  ; check the symbol only, ignoring what it's bound to
            cond
              (eq? prev-op 'none)     ; init
                loop op-sym list(x acc op) rest-in
              (eq? op-sym prev-op)    ; buffer and continue
                loop op-sym (cons x acc) rest-in
              else                    ; buffer done, flip it now and re-init here with this op-sym
                loop 'none (reverse acc) stxs-in
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
  define infix-to-prefix-with-precedence(stx ctx-stx)  ; ctx-stx context for error reporting
    define result
      for/fold
        ([acc (syntax->list stx)])
        ([grp sym-groups])
        reduce-given-ops grp acc
    match result
      (cons x '())  ; the final result should be a one-element list (of nested syntax objects)
        datum->syntax stx x
      (cons x xs)   ; the tail, if any, contains at least one term that did not process correctly.
        define msg
          match xs
            (cons xs0 xss)
              format "~a" (syntax->datum xs0)
            else  ; fallback: show erroneous expr, usually partly transformed
              format "in ~a" (datum->syntax stx result)
        raise-syntax-error 'infix (format "unknown operator ~a" msg) stx ctx-stx

;; Reduce on given operators (symbols) only, pass the rest of stx-list through as-is.
;; Here stx-list is an infix expression represented as a list of syntax objects.
;;
;; To figure out how this works, consider how it processes these with op-syms (list * /):
;;   1 + 2 + 3 * 4 * 5 + 6
;;   1 * 2 / 3 * 4 + 5 + 6
begin-for-syntax
  define reduce-given-ops(op-syms stx-list)
    define rev(x) (cond [(pair? x) (reverse x)] [else x])
    define loop(prev-op buffer stxs-in acc)  ; here prev-op tracks only ops in target-ops
      match stxs-in
        '()
          define final-acc (cons (rev buffer) acc)  ; commit the last buffer
          reverse final-acc
        (list-rest op x rest-in)
          let ([op-sym (syntax->datum op)])
            cond
              (member op-sym op-syms)
                cond
                  (eq? prev-op 'none)
                    loop op-sym list(x buffer op) rest-in acc  ; init buffer
                  (eq? op-sym prev-op)
                    loop op-sym (cons x buffer) rest-in acc    ; same op-sym - buffer and continue
                  else  ; different op-sym but still ours
                    loop 'none (rev buffer) stxs-in acc     ; buffer done, re-init with this op-sym
              else  ; commit buffer
                ;; we must set prev-op to 'none here to trigger init in case the next op-sym
                ;; turns out to be interesting.
                define cons-args-to(tgt . args) (foldl cons tgt args)
                loop 'none x rest-in (cons-args-to acc (rev buffer) op)
    ;; If stx-list has only one element, do nothing; this catches cases like {x * y expt z},
    ;; where "x0" <- (* x (expt y z)), and "terms" is empty, right away when we are called for (+ -).
    ;;
    ;; loop() would reverse the only subexpr, since we construct all else with cons and reverse.
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
