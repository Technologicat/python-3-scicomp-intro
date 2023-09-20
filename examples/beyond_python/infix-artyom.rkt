#lang racket

;; Elegant, simple infix arithmetic with precedence, from Artyom Kazak's "Learning Racket" blog post series, 2020, since defunct.
;;   https://web.archive.org/web/20201121162125/https://artyom.me/learning-racket-1
;;   https://web.archive.org/web/20201121162132/https://artyom.me/learning-racket-2
;; The infix macro is in part 2, and is there called ":". The best bet is to Ctrl+F for "expt".

(require (for-syntax syntax/parse))

(define-syntax (nfx stx)
  (syntax-parse stx #:datum-literals (+ - * / ^)
    [(_ l ... + r ...) #'(+ (nfx l ...) (nfx r ...))]
    [(_ l ... - r ...) #'(- (nfx l ...) (nfx r ...))]
    [(_ l ... * r ...) #'(* (nfx l ...) (nfx r ...))]
    [(_ l ... / r ...) #'(/ (nfx l ...) (nfx r ...))]
    [(_ l     ^ r ...) #'(expt l        (nfx r ...))]  ; expt is right-associative
    [(_ x)             #'x]))  ; base case

;; equal? ≈ Python's "=="
;; eq? ≈ Python's "is"
;; = - numerical equality

(if
  (let [(a (nfx 1 + 3 - (+ 1 2 3) * 4 / 5 + 3 * 7 ^ 2 ^ 2 * 5 - 3 / 5 / 8 - 9 / 7))
        (b (+ 36012 (/ 47 56)))]
    (= a b))
  'pass
  (error "test failed"))
