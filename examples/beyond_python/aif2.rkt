#lang sweet-exp racket

;; The classic anaphoric if.
;;
;; The modern rackety way to not-really break hygiene, while achieving similar effect,
;; is to use syntax parameters. This way no new bindings need to be introduced.
;;
;; See the docs for (syntax-parameterize) and the paper
;; http://scheme2011.ucombinator.org/papers/Barzilay2011.pdf

require syntax/parse/define
require racket/stxparam

provide aif it

;; This is the only binding for "it"; we will just dynamically adjust what it points to.
define-syntax-parameter it
  syntax-parser
    _
      raise-syntax-error 'it "only meaningful inside aif" this-syntax

define-syntax-parser aif
  [_ test then else]
    syntax
      let ([t test])
        syntax-parameterize ([it (syntax-parser (_ #'t))])
          if t then else

module+ main
  aif (* 2 5) it #f

