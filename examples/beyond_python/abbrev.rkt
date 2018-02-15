#lang sweet-exp racket

;; Using the power of syntax to abbreviate names, including those of other syntactic constructs.

;; abbreviation
;; https://stackoverflow.com/questions/26596974/macro-defining-macro-in-racket

require (for-syntax syntax/parse)
require syntax/parse/define
provide abbrev

;; as posted by soegaard (here using syntax-parse instead of syntax-case):
define-syntax-parser abbrev
  [(_ long short) #'(define-syntax short make-rename-transformer(#'long))]

module+ main
  abbrev define def
  def f(x)
    * x x
  f(3)

;; This also works (as posted by uselpa).
;;
;; The only non-obvious part of its definition is the (... ...),
;; which “quotes” ... so that it takes its usual role in the
;; generated macro, instead of the generating macro.
;;    --Racket Guide (but old version, this example is no longer there)
;;      http://docs.racket-lang.org/guide/pattern-macros.html#%28part._.Macro-.Generating_.Macros%29
;;
define-syntax-rule (abbrv long short)
  define-syntax-rule (short body (... ...)) (long body (... ...))

module+ main
  abbrv define df
  df g(x)
    + x x
  g(3)

;; One more way - complicated but demonstrates another feature.
;;
;; When nesting syntax-parse, we must escape any ... that is intended
;; for the inner syntax-parse; otherwise the outer one will capture it.
;;
;; There are two ways to do this:
;;   - use (... ...); a block that begins with "(..." treats ... literally
;;       https://lists.racket-lang.org/users/archive/2010-July/040767.html
;;       https://stackoverflow.com/a/38276125
;;   - using quote-syntax, create a constant representing a literal ellipsis
;;       https://stackoverflow.com/a/38276476
;;
;; Note also:
;;
;; define-syntax-parser foo
;;   ...
;;
;; roughly means
;;
;; define-syntax foo
;;   syntax-parser
;;     ...
;;
;; which in turn roughly means
;;
;; define-syntax foo(stx)
;;   syntax-parse stx
;;     ...
;;
;; In the forms without an explicit "stx", the input syntax object can be accessed as "this-stx".
define-syntax abbr(stx)                   ; Can't use define-syntax-parser here; need to insert...
  with-syntax ([ooo (quote-syntax ...)])  ; ...this between the define and the syntax-parse.
    syntax-parse stx  ; When the macro "abbr" is called with a syntax object...
      (_ long short)  ; ...the notation "abbr long short" expands to...
        syntax        ; ...the following syntax:
          define-syntax-parser short        ; ...that defines a new syntax parser, "short"...
            (_ body ooo) #'(long body ooo)  ; ...which expands to "long", passing through all args.

module+ main
  abbr define d
  d h(x)
    expt x x
  h(3)
