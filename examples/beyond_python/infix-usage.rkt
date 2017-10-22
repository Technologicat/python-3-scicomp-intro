#lang sweet-exp racket

;; usage example for infix-handler.rkt

require "infix-handler.rkt"

module+ main
  {2 + 3 * 4}  ; (2 + 3) * 4
  {2 * 3 + 4}  ; (2 * 3) + 4
