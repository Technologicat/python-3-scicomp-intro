#lang racket

;; Minimalistic pythonic import.
;;
;; A compromise between the Zen minimalism of Racket and the readability of Python.
;; Makes the package name explicit at the use site, and imports the specified forms only.
;;
;; Summary::
;;     (require (from modname id0 ...))                        ; --> modname:id0
;;     (require (from modname [id0 asname0] ...))              ; --> modname:asname0
;;     (require (from [modname asmodname] id0 ...))            ; --> asmodname:id0
;;     (require (from [modname asmodname] [id0 asname0] ...))  ; --> asmodname:asname0
;;
;; Hopefully the abstraction is transparent enough to be understandable from usage,
;; without even looking at this file.
;;
;; The point is to make imports explicit (like in Python) right in your favorite text editor,
;; without requiring an IDE with a bindings tracking overlay (like DrRacket).

;; -------------------------------------------------------------------------------------------------
;; Implementation

(provide from)

;; The whole point is to say things like this more briefly:
(require (for-syntax (prefix-in sp: (only-in syntax/parse syntax-parse))))        ; (require (for-syntax (from [syntax/parse sp] syntax-parse)))
(require (for-syntax (prefix-in rs: (only-in racket/syntax format-id))))          ; (require (for-syntax (from [racket/syntax rs] format-id)))
(require (prefix-in rrs: (only-in racket/require-syntax define-require-syntax)))  ; (require (from [racket/require-syntax rrs] define-require-syntax)

;; Given a syntax object `stx` for representing an identifier "id", suffix a colon to the identifier, and return
;; a new syntax object with textual representation "id:", with lexical context and source location of `ctx`.
(define-for-syntax (make-prefix-identifier ctx stx)
  (rs:format-id ctx #:source ctx "~a:" (syntax-e stx)))  ; (format-id lexical-context #:source source-location format value)

;; The actual `from` form.
;; We pass `id0 ...` through to the underlying `require` form to support things like `[id0 asname0]`.
(rrs:define-require-syntax (from stx)
  (sp:syntax-parse stx
                   [(_ [modname asmodname] id0 ...)
                    (with-syntax [(pfx (make-prefix-identifier stx #'asmodname))]
                      #'(prefix-in pfx (only-in modname id0 ...)))]
                   [(_ modname id0 ...)
                    (with-syntax [(pfx (make-prefix-identifier stx #'modname))]
                      #'(prefix-in pfx (only-in modname id0 ...)))]))

;; -------------------------------------------------------------------------------------------------
;; Unit tests

(module+ main
  ;; Just test that each usage example completes without errors.
  ;; Here we use `syntax-parse` from module `syntax/parse` just for illustration.
  (require (from syntax/parse syntax-parse))  ; -> modname:id, e.g.. syntax/parse:syntax-parse
  (if (identifier-binding #'syntax/parse:syntax-parse) 'pass (error "basic from-import test failed"))
  
  (require (from syntax/parse [syntax-parse s-parse]))  ; -> modname:asname, e.g. syntax/parse:s-parse
  (if (identifier-binding #'syntax/parse:s-parse) 'pass (error "asname from-import test failed"))
  
  (require (from [syntax/parse sp] syntax-parse))  ; -> asmodname:id, e.g. sp:syntax-parse
  (if (identifier-binding #'sp:syntax-parse) 'pass (error "asmodname from-import test failed"))
  
  (require (from [syntax/parse sp] [syntax-parse s-parse]))  ; -> asmodname:asname, e.g. sp:s-parse
  (if (identifier-binding #'sp:s-parse) 'pass (error "asmodname:asname from-import test failed")))
