#lang sweet-exp racket

;; Simple pythonic generators in Racket, using call/cc.
;;
;; NOTE: Racket already provides racket/generator, which can do this and much more.
;;
;;       This is meant as an example of how generators work, and how they can be
;;       defined using call/cc (or its cousin let/cc, which we actually use here).

require "return.rkt"  ; return statement - also based on call/cc 

;; Barebones example with a hardcoded body
define instantiate-generator1()
  let ([k 'none])
    λ/return ()  ; <-- in Python terms, this is the next() method
      cond
        (not (eq? k 'none))  ; resume?
          k()
      let loop ([x 0])
        ;; Perform a yield manually:
        let/cc cc    ; capture the continuation of this block
          set! k cc  ; save it
          return x   ; exit by returning a value
        loop {x + 1}

;; Still hardcoded body, but with yield as a procedure:
define instantiate-generator2()
  let ([k 'none])
    λ/return ()
      let ([yield (λ (value)
                        (let/cc cc
                          (set! k cc)
                          (return value)))])
        cond
          (not (eq? k 'none))  ; resume?
            k()
        let loop ([x 0])
          yield x
          loop {x + 1}

;; Finally, extracting the design pattern as a macro:
require syntax/parse/define

define-syntax yield(. args)  ; outside a generator, make "yield" a compile-time syntax error
  raise-syntax-error 'yield "only meaningful inside a generator body"

define-syntax-parser make-generator
  (_)
    raise-syntax-error 'make-generator "missing body"
  ;; here we actually need access to the syntax-object representing the make-generator form itself,
  ;; so we give it a name ("mg").
  (mg body ...)
    with-syntax ([yield (datum->syntax #'mg 'yield)])  ; break hygiene, providing the name "yield"
      syntax
        let ([k 'none])
          λ/return ()
            let ([yield (λ args  ; bind the name "yield" to its implementation
                            (let/cc cc
                              (set! k cc)
                              (apply return args)))])
              cond
                (not (eq? k 'none))  ; resume?
                  k()
              body
              ...

;; Examples:
module+ main
  define g1 instantiate-generator1()
  g1()
  g1()
  g1()
  ;
  define g2 instantiate-generator2()
  g2()
  g2()
  g2()
  ;
  define g3
    make-generator  ; inside the body here, we have "yield" available; it works like in Python.
      let loop ([x 42])
        yield x
        loop {x + 1}
  g3()
  g3()
  g3()
  ;
  define g4
    make-generator
      'hello  ; we can put any code here; if there's no "yield", all of it simply re-runs each time
  g4()
  g4()
  g4()
