#lang sweet-exp racket

;; Return. In Racket, obviously only has a use for early exit.
;;
;; return 'whatever
;; return 1 2 3  ; behaves like a normal exit with values(1 2 3);
;;               ; this is due to the semantics of call/cc.
;;
;; With thanks to Matthew Might.
;; http://matt.might.net/articles/implementing-exceptions/

provide return define/return lambda/return λ/return

require for-syntax(syntax/parse)
require only-in("abbrev.rkt" abbrev)

define-syntax return(stx)
  raise-syntax-error('return "not meaningful outside {define,λ,lambda}/return forms" stx)

define-syntax define/return(stx)
  syntax-parse stx
    (_ (f args ...) body ...)
      with-syntax ([return datum->syntax(stx 'return stx)])  ; make "return" visible to user code...
        syntax
          define (f args ...)
            let/ec return  ; ...and bind it to the ec
              body
              ...

define-syntax lambda/return(stx)
  syntax-parse stx
    (_ args body ...)
      with-syntax ([return datum->syntax(stx 'return stx)])
        syntax
          λ args
            let/ec return
              body
              ...

abbrev lambda/return λ/return

module+ main
  define/return f(x)
    displayln("hello from f")
    return (* x x)
    displayln("not reached")
  f(5)
  define g (λ/return (x) (return (* x x)))
  g(5)
