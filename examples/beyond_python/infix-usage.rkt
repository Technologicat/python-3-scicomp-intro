#lang sweet-exp racket

;; usage example for infix-handler.rkt

;require "infix-handler.rkt"  ; always left-to-right
require "infix-handler2.rkt"  ; simple math rules for + - * / expt

module+ main
  {2 * 3 + 4}    ; both: (2 * 3) + 4 = 10
  {2 + 3 * 4}    ; nfx1: (2 + 3) * 4 = 20, left-to-right
                 ; nfx2: 2 + (3 * 4) = 14, usual math precedence
  {5 * 2 expt 5} ; nfx1: (5 * 2) expt 5 = 10⁵
                 ; nfx2: 5 * (2 expt 5) = 160
  ;; Can also call functions in the expressions.
  {1 + 2 * log(5)}
  {2 * log(5) + 1}
