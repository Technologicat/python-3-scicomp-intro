#!/usr/bin/env racket
#lang sweet-exp racket

;; See Racket Guide, sec. 4.5.
;; https://docs.racket-lang.org/guide/define.html

;; To define functions, usually one uses this shorthand:
define myfunc1(x)
  {2 * x}

;; Which is equivalent to:
define myfunc2 (λ (x)
  {2 * x})

;; i.e. by using indentation in sweet-exp:
define myfunc3
  λ (x) {2 * x}

;; or even:
define myfunc4
  λ (x)
    {2 * x}

;; For the curious: look at the source in the Macro Stepper in DrRacket:
;;   - myfunc2 through myfunc4 expand to the same code.
;;   - All four versions internally expand to the same code
;;     (to see this, disable macro hiding in Macro Stepper).

myfunc1(10)
myfunc2(10)
myfunc3(10)
myfunc4(10)
