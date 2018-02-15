#lang sweet-exp racket

;; Pythonic while-else.
;;
;; See also dyoo-while-loop in the Racket repo, which provides
;; similar functionality, but without the else block.
;;
;; With thanks to Matthew Might.
;; http://matt.might.net/articles/implementing-exceptions/

;; TODO: test break(value) -> should return it to outside the loop

provide while break continue

require for-syntax(syntax/parse)

define-syntax continue(stx)
  raise-syntax-error('continue "not meaningful outside 'while'" stx)

define-syntax break(stx)
  raise-syntax-error('break "not meaningful outside 'while'" stx)

define-syntax while(stx)
  syntax-parse stx
    #:datum-literals (else)
    (_ condition body ... else expr ...)
      with-syntax ([break datum->syntax(stx 'break stx)]
                   [continue datum->syntax(stx 'continue stx)])
        syntax
          let/ec break
            define loop()
              cond
                condition
                  let/ec continue
                    body
                    ...
                  loop()
                else
                  expr
                  ...
            loop()
    (_ condition body ...)
      syntax
        while condition body ... else (void)

module+ main
  define i 0
  ;
  set! i 0
  while {i < 5}  ; note that the indentation is a bit different from Python...
    set! i {i + 1}
    displayln i
    else         ; ...because the "else" must be an argument to the "while".
    displayln "runs when done"
  ;
  set! i 0
  while {i < 5}
    set! i {i + 1}
    displayln i
    cond [{i = 3} break()]
    else
    displayln "does not run because we break()"
  ;
  set! i 0
  while {i < 5}
    set! i {i + 1}
    cond [{i = 3} continue()]
    displayln i
    else
    displayln "runs when done"
