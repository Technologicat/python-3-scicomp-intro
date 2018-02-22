#lang sweet-exp typed/racket

;; In Racket 6.10.1, refined types seem to detect correctly at runtime, but not at compile time.
;;
;; This is a new feature in 6.11, which was experimental in 6.10.1.
;;  https://www.infoq.com/news/2017/11/racket-6-11-dependent-types

define-type Over9000 (Refine [n : Integer] (> n 9000))
define-predicate over9000? Over9000

: test (-> Over9000 Any)
define test(x)
  displayln over9000?(x)

module+ main
  test 8001
  test 9001
