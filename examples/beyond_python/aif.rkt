#lang sweet-exp racket

;; The classic anaphoric if.
;;
;; This locally binds the identifier "it" to the result of the test expression.
;;
;; (Note that Racket's cond already supplies the => operator with similar functionality.)

require (for-syntax syntax/parse)

provide aif it

;; The identifier "it" is only meaningful inside an "aif" form, so we make it raise a syntax error
;; if used elsewhere.
define-syntax it(stx) raise-syntax-error('it "only meaningful inside aif" stx)

;; The with-syntax exposes the identifier "it" to the expanded form of the macro,
;; avoiding the automatic renaming (that Racket usually applies to respect lexical scope).
;;
;; Search terms: "hygienic macros"; "breaking hygiene".
;;
;; This makes the identifier "it" visible, but it is still unbound. The let then binds "it"
;; to the value of the test expression, for the lexical scope of the let block.
;;
define-syntax aif(stx)
  syntax-parse stx
    [(_ test:expr true-branch:expr false-branch:expr)
     (with-syntax ([it (datum->syntax #'test 'it)])
       #'(let ([it test])
            (if it true-branch false-branch)))]

module+ main
  aif (* 2 5) it #f
