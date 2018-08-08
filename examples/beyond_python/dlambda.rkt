#lang sweet-exp racket

require syntax/parse/define
require "abbrev.rkt"

provide dlambda λ/dispatch define-dispatcher

;; Dispatching λ, for easily making closures with multiple methods.
;;
;; Inspired by Doug Hoyte's Let Over Lambda: 50 Years of Lisp.
;; Racketified.
;;
;; argspec like in λ.
;;
;; Default action is for calling the dispatcher normally, without any "#:m method-name".
;; The default default-action is a 0-argument function that just returns #f.
;;
;; Minimal introspection: use "#:m '?" to get a list of action names defined in a particular instance.
define-syntax-parser dlambda
  #:datum-literals (else)
  [_ (action:id argspec body ...) ... (else else-argspec else-body ...)]
    syntax
      ; '() is not an id, so it always falls through to the default case.
      λ (#:m [name '()] . args)  ; dispatcher
        define action
          λ argspec
            body
            ...
        ...
        define default-action
          λ else-argspec
            else-body
            ...
        define all-action-names (list (quote action) ...)  ; minimal introspection support
        cond
          {name eq? '?}
            all-action-names
          {name eq? (quote action)}
            apply action args
          ...
          else
            apply default-action args
  ; provide a default else clause
  [this-stx (action:id (arg ...) body ...) ...]
    syntax
      this-stx (action (arg ...) body ...) ... (else () #f)

;; Abbreviated form. Note the method definitions still use the same syntax as in dlambda.
define-syntax-parser define-dispatcher
  [_ dispatcher-name stuff ...]
    syntax
      define dispatcher-name
        λ/dispatch stuff ...

abbrev dlambda λ/dispatch

module+ main
  ;; We want to achieve something like this:
  define f1
    λ (#:m [name '()] . args)
      cond
        {name eq? 'hello}
          displayln "hello"
        {name eq? 'hi}
          displayln "hi"
        {name eq? 'disp}
          displayln (car args)
        else
          #f
  ;
  ;; We can easily generate something like this:
  define f2
    λ (#:m [name '()] . args)
      define hello
        λ ()
          displayln "hello"
      define hi
        λ ()
          displayln "hi"
      define disp
        λ (s)
          displayln s
      cond
        {name eq? 'hello}
          (apply hello args)
        {name eq? 'hi}
          (apply hi args)
        {name eq? 'disp}
          (apply disp args)
        else
          #f
  ;
  ;; Automated macro version:
  define f3
    λ/dispatch
      hello ()             ; action-name argspec
        displayln "hello"  ; body
      hi ()
        displayln "hi"
      disp (s)
        displayln s
      else args            ; default action, here with varargs (see λ)
        displayln args
  ;
  ; abbreviated form
  define-dispatcher f4
    hello ()             ; action-name argspec
      displayln "hello"  ; body
    hi ()
      displayln "hi"
    disp (s)
      displayln s
    else args            ; default action, here with varargs (see λ)
      displayln args
  ;
  ; testing without the else clause
  define-dispatcher f5
    hello ()             ; action-name argspec
      displayln "hello"  ; body
    hi ()
      displayln "hi"
    disp (s)
      displayln s
  ;
  (f1 #:m 'hello)
  (f1 #:m 'disp "foo")
  (f1 "baa" "goes" "the" "sheep")
  ;
  (f2 #:m 'hello)
  (f2 #:m 'disp "foo")
  (f2 "baa" "goes" "the" "sheep")
  ;
  (f3 #:m 'hello)
  (f3 #:m 'disp "foo")
  (f3 "baa" "goes" "the" "sheep")
  ;
  (f4 #:m 'hello)
  (f4 #:m 'disp "foo")
  (f4 "baa" "goes" "the" "sheep")
  ;
  (f5 #:m 'hello)
  (f5 #:m 'disp "foo")
  (f5 #:m '?)  ; ask what actions f5 has
