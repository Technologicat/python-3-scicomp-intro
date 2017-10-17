#!/usr/bin/env racket
#lang sweet-exp racket

;; What makes LISP different:
;;
;; In LISP, programs can modify the *language syntax*.
;;
;; For example, the core of LISP doesn't even define a for loop, but if we:
;;
define-syntax-rule (for-range (v start end) body ...)
  let ([vlast {end - 1}])
    let do-one ([v start])
      body
      ...
      cond [{v < vlast} do-one{v + 1}]  ; loop by tail recursion

;; (This is properly called a macro, which LISP then expands when compiling or running the program.
;;
;;  But don't be confused, LISP macros are much more powerful than macros in other programming
;;  languages (e.g. C preprocessor macros).)

;; We can then:
;;
for-range (i 0 5)
  displayln i  ; i is visible here, as this part goes into the function body
  displayln "hi"
;; ...and out here, i no longer exists.

;; Modern LISP dialects, such as Racket that is used here, do define a for loop,
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
