#!/usr/bin/env racket
#lang sweet-exp racket

;; In these notes, to improve code readability, we will use sweet-expressions (t-expressions).
;;
;; This Lisp extension provides infix notation for operators, natural function call syntax,
;; and the possibility to replace some parenthesization by consistent indentation (à la Python).
;;
;; For Racket, the sweet-exp extension is written in the Racket language, just like any program.
;;
;; It patches the reader layer that turns the source code into the data-structure representation
;; for processing by the expander layer.
;;
;; http://docs.racket-lang.org/guide/Pairs__Lists__and_Racket_Syntax.html#%28part._lists-and-syntax%29
;; http://docs.racket-lang.org/guide/languages.html

;; Sweet-exp for Racket:
;;
;;   https://docs.racket-lang.org/sweet/
;;
;; Original "Readable s-expressions" module for guile (another Scheme dialect) and Common Lisp:
;;
;;   https://sourceforge.net/p/readable/wiki/Solution/
;;
;; The {} infix notation has been accepted as SRFI-105:
;;
;;   https://srfi.schemers.org/srfi-105/srfi-105.html
;;
;; Sweet expressions (t-expressions), i.e. all other parts of the extension,
;; have been accepted as SRFI-110:
;;
;;   https://srfi.schemers.org/srfi-110/srfi-110.html

;; sweet-exp in a nutshell:
;;
;;   - Infix notation:
;;       {2 * 3 * 4}  -->  (* 2 3 4)
;;
;;     but if different operators, must group manually (*by design*, the {} notation has no
;;     concept of operator precedence; see https://sourceforge.net/p/readable/wiki/Precedence/ ):
;;
;;       {2 + {3 * 4}}
;;
;;   - Usually, implicit parentheses around each line:
;;
;;       define x 2  -->  (define x 2)
;;
;;     but this is disabled when inside (), [] or {}, so expressions inside constructs such as
;;     cond  and  let  will need to use explicit parentheses.
;;
;;   - A sequence of newline and indentation creates a parenthesized group, like this:
;;       define x
;;         * 2 3
;;     -->
;;       define x (* 2 3)
;;     -->
;;       (define x (* 2 3))  ; by previous rule; final form
;;
;;   - Implicit parenthesization can also be overridden by explicitly using parentheses.
;;
;;   - More groups can be added to the same level by using the same amount of indentation:
;;       if {x < 1}
;;         #t
;;         #f
;;     -->
;;       if {x < 1} (#t) (#f)
;;
;;   - Note that by the previous rules, the above example further transforms to:
;;     -->
;;       if (< x 1) (#t) (#f)    ; convert infix notation to prefix notation
;;     -->
;;       (if (< x 1) (#t) (#f))  ; parenthesize the whole expression; final form
;;
;;   - E.g. "for" in Racket allows for several index variables (stepping in sync), so the
;;     definition block for these must be surrounded by extra parentheses (so that it can be
;;     treated exactly the same regardless of whether there is just one or several index variables).
;;     Similarly, "let" (local binding) can define several variables at once, so the same requirement.
;;
;;   - These are equivalent:
;;       f(arg1 arg2)   ; t-expression style. Note no space between f and the opening parenthesis.
;;       (f arg1 arg2)  ; s-expression (standard Scheme) style.
;;
;;     Basically, f(arg1 arg2 ...) becomes (f arg1 arg2 ...); keep this in mind when reading the code.

define factorial(n)
  if {n <= 1}
    1
    {n * factorial{n - 1}}

; Racket's module system provides a mechanism for a conditional main, like in Python:
;
; https://docs.racket-lang.org/guide/Module_Syntax.html
;
module+ main
  factorial(10)

;; Standard Scheme (s-expressions).
;;
;; - everything must be parenthesized explicitly
;; - considered polite toward other programmers to use indentation (but the computer doesn't care)
;; - function calls are written as (f arg1 arg2 ...)
;; - operators use prefix notation: (operator op1 op2 ...)
;; - a module system was introduced in RSR6 scheme, but we'll skip that here.
;;
;;(define (factorial n)
;;  (if (<= n 1)
;;    1
;;    (* n (fact (- n 1) ))))
;;
;;(factorial 10)
