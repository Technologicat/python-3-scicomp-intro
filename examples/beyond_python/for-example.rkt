#lang sweet-exp racket

;; https://docs.racket-lang.org/guide/for.html

define L '(1 6 2 5 4 8 9 7 3 0)

for ([x L])    ;; Python: for x in L:
  displayln x
