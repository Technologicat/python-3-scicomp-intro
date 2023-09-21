#lang racket

;; Elegant, simple infix arithmetic with precedence, from Artyom Kazak's "Learning Racket" blog post series, 2020, since defunct.
;;   https://web.archive.org/web/20201121162125/https://artyom.me/learning-racket-1
;;   https://web.archive.org/web/20201121162132/https://artyom.me/learning-racket-2
;; The infix macro is in part 2, and is there called ":". The best bet is to Ctrl+F for "expt".
;;
;; SRFI-105 (curly infix expressions) hooks into a user-defined macro named "$nfx$", so we use that name.
;;   https://srfi.schemers.org/srfi-105/srfi-105.html

;; -------------------------------------------------------------------------------------------------
;; Implementation

(provide $nfx$)

(require (for-syntax (prefix-in sp: (only-in syntax/parse syntax-parse))))

(define-syntax ($nfx$ stx)
  (sp:syntax-parse stx #:datum-literals (+ - * / ^)
    [(_ l ... + r ...) #'(+ ($nfx$ l ...) ($nfx$ r ...))]
    [(_ l ... - r ...) #'(- ($nfx$ l ...) ($nfx$ r ...))]
    [(_ l ... * r ...) #'(* ($nfx$ l ...) ($nfx$ r ...))]
    [(_ l ... / r ...) #'(/ ($nfx$ l ...) ($nfx$ r ...))]
    [(_ l     ^ r ...) #'(expt l          ($nfx$ r ...))]  ; expt is right-associative
    [(_ x)             #'x]))  ; base case

;; -------------------------------------------------------------------------------------------------
;; Unit tests

;; Racket's most common equality operators:
;;   equal?   ≈ roughly, Python's "==", with a default of "is" if not customized for a given datatype, just like in Python.
;;   eq?      ≈ Python's "is"
;;   =        - numerical equality

(module+ main
  (if
   ;; Note the `(+ 1 2 3)` is passed through as-is.
   (let [(a ($nfx$ 1 + 3 - (+ 1 2 3) * 4 / 5 + 3 * 7 ^ 2 ^ 2 * 5 - 3 / 5 / 8 - 9 / 7))
         (b (+ 36012 (/ 47 56)))]
     (= a b))
   'pass
   (error "test failed")))

  ;; Show the expansion process for a simple example.
  (let [(e #'($nfx$ 1 - (+ 1 2 3)))]
    (for [(i (in-range 10))]
      (displayln e)
      (set! e (expand-once e)))
    (if (= (eval e) -5) 'pass (error "test failed")))
