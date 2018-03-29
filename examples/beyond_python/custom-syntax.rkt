#!/usr/bin/env racket
#lang sweet-exp racket

;; What makes Lisp different:
;;
;; In the Lisp family, programs can modify the *language syntax*.
;;
;; For example, the core language doesn't even define a for loop, but if we:
;;
define-syntax-rule (for-range (v start end) body ...)
  let ([vlast {end - 1}])
    let do-one ([v start])
      body
      ...
      cond [{v < vlast} do-one{v + 1}]  ; loop by tail recursion

;; (This is properly called a macro, which is then *expanded* when compiling or running the program.
;;
;;  Note that Lisp macros are *syntactic macros* - much more powerful than e.g. C preprocessor macros.
;;  Whereas preprocessor macros perform string replacement, a syntactic macro runs arbitrary code to
;;  transform the AST (abstract syntax tree).)

;; With the for-range macro, we can:
;;
for-range (i 0 5)
  displayln i  ; i is visible here, as this part goes into the function body
  displayln "hi"
;; ...and out here, i no longer exists.

;; Modern Lisp dialects, such as Racket that is used here, do define a for loop,
;; but it is a part of the standard library, not of the language core.

;; -------------------------------------------------------------------------------------

;; For the curious, the above "named let" is equivalent to:
;
;define-syntax-rule (for-range (v start end) body ...)
;  letrec ([vlast {end - 1}]  ; use letrec so the id "do-one" is created before evaluating its def
;          [do-one (λ (v)
;                    body
;                    ...
;                    cond([{v < vlast} do-one{v + 1}]))])  ; loop by tail recursion
;      do-one(start)

;; -------------------------------------------------------------------------------------

;define-syntax-rule (my-for (v start end) body ...)
;  letrec ([max {end - 1}]
;          [loop (λ (v)
;                  body
;                  ...
;                  (if {v >= max}
;                      null
;                      loop{v + 1}))])
;      loop(start)

;define-syntax-rule (my-for (v start end) body ...)
;  letrec ([vlast {end - 1}]  ; use letrec so the id "do-one" is created before evaluating its def
;          [do-one (λ (v)
;                    body
;                    ...
;                    (cond [{v < vlast} do-one{v + 1}]))])  ; loop by tail recursion
;      do-one(start)

