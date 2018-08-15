#lang sweet-exp racket

;; alet: capture and export the last subform of body as "this".
;;
;; Inspired by Doug Hoyte's Let Over Lambda: 50 Years of Lisp.
;; Racketified.

require syntax/parse/define
require "abbrev.rkt"

provide alet let/anaphoric this alet-fsm state

define-syntax this(stx) raise-syntax-error('this "only meaningful inside alet" stx)
define-syntax state(stx) raise-syntax-error('state "only meaningful inside alet-fsm" stx)

;; Like let, but the last subform of body (lastbody) is evaluated first, and bound to "this"
;; in the scope where the other subforms of body are evaluated.
;;
;; Useful especially when lastbody is a lambda.
;;
define-syntax-parser alet0
  [this-stx ([k:id v] ...) body ... lastbody]
    with-syntax ([this (datum->syntax #'this-stx 'this)])  ; break hygiene
      syntax
        let ([k v] ...)
          define this lastbody
          body
          ...
          this
  ;; make values optional:
  ;; name-only decls at the end, insert 'none as value, apply base case
  [this-stx ([k0:id v0] ... k1 ...) body ...]
    #'(this-stx ([k0 v0] ... [k1 'none] ...) body ...)
  ;; move any name-only decls from the front to after the first with-value decls, retry
  ;; (here the maybe-more decls can be either format)
  [this-stx (k0:id ... [k1:id v1] ... maybe-more ...) body ...]
    #'(this-stx ([k1 v1] ... k0 ... maybe-more ...) body ...)
  ;; move name-only decls from between two with-value decl groups to after the second group, retry
  [this-stx ([k0:id v0] ... k1:id ... [k2:id v2] ... maybe-more ...) body ...]
    #'(this-stx ([k0 v0] ... [k2 v2] ... k1 ... maybe-more ...) body ...)

;; Callable may refer to a mutable variable. Wrapper to look up and use the current value.
define-syntax-parser wrap
  [_ callable]
    syntax
      make-keyword-procedure
        λ (kw kv . args)
          keyword-apply callable kw kv args
        λ　args
          apply callable args

;; Like alet0, but with indirection, so that lastbody may "set! this ..."
;; and it will change the stored procedure.
;;
;; (In alet0, the issue is that the let form returns **the original** "this"
;;  to the caller, so modifying the local binding of "this" won't update the caller's copy.
;;  Here the caller instead gets a wrapper that looks up and uses whatever "this" is
;;  currently pointing to.)
define-syntax-parser alet
  [this-stx ([k:id v] ...) body ... lastbody]
    with-syntax ([this (datum->syntax #'this-stx 'this)])  ; break hygiene
      syntax
        let ([k v] ...)
          define this lastbody
          body
          ...
          wrap this  ; <-- only difference to alet0.
  ;; make values optional
  [this-stx ([k0:id v0] ... k1 ...) body ...]
    #'(this-stx ([k0 v0] ... [k1 'none] ...) body ...)
  [this-stx (k0:id ... [k1:id v1] ... maybe-more ...) body ...]
    #'(this-stx ([k1 v1] ... k0 ... maybe-more ...) body ...)
  [this-stx ([k0:id v0] ... k1:id ... [k2:id v2] ... maybe-more ...) body ...]
    #'(this-stx ([k0 v0] ... [k2 v2] ... k1 ... maybe-more ...) body ...)

abbrev alet let/anaphoric

;; finite state machine / flying spaghetti monster
;;
;; Only meaningful inside alet.
;;
;; Binds "state" to a procedure that re-binds "this". Otherwise a bit similar to λ/dispatch.
;; See example below.
;;
;; Note that at the module level, "this" has been defined as a syntax that just errors out,
;; to prevent misuse; it is also a class keyword in the standard library. We use with-syntax
;; to point "this" to the third, intended definition, which falls in lexically from the
;; surrounding alet form (so copying the lexical context from #'this-stx, we're fine).
;;
define-syntax-parser alet-fsm
  [this-stx (state0:id argspec0 body0 ...) (state1:id argspec1 body1 ...) ...]
    with-syntax ([state (datum->syntax #'this-stx 'state)]
                 [this (datum->syntax #'this-stx 'this)])
      syntax
;        let-syntax  ; Hoyte's original uses a macro here.
;          \\
;            state
;              λ (stx)
;                syntax-parse stx
;                  [_ s] #'(set! this s)
        let   ; It seems in Racket we can use a regular procedure here.
          \\  ; Will evaluate "s" at call time, but probably fine?
            state
              λ (s)
                set! this s
          letrec
            \\
              state0 (λ argspec0 body0 ...)
              state1 (λ argspec1 body1 ...)  ; must be spelled out with two states...
              ...
            state0  ; ...because no "..." after state0 here.

;; For the examples.
define-syntax-parser update!
  [_ target op value]
    syntax
      begin
        set! target {target op value}
        target
define-syntax-parser inc!
  [_ target value] #'(update! target + value)
define-syntax-parser dec!
  [_ target value] #'(update! target - value)

module+ main
  require "dlambda.rkt"
  define f
    alet0 (s p e)
      this #:m 'reset
      λ/dispatch
        reset ()
          set! s 0
          set! p 1
          set! e 2
        else (n)
          set! s {s + n}
          set! p {p * n}
          set! e {e expt n}
          list s p e
  ;
  for/list ([i in-range(5)])
    f 2
  f #:m 'reset
  for/list ([i in-range(5)])
    f 0.5
  ;
  ;; The full alet lets us "set! this ...".
  require "alambda.rkt"
  define g
    alet ([acc 0])
      λ/anaphoric (n)  ; <-- self points here
        cond
          {n eq? 'invert}
            set! this
              λ (n)
                cond
                  {n eq? 'invert}
                    set! this self
                  else
                    dec! acc n
          else
            inc! acc n
  g 10
  g 'invert
  g 3
  ;
  ;; which is a horribly convoluted way of saying:
  define g2
    alet ([acc 0])
      letrec
        \\
          going-up
            λ (n)
              cond
                {n eq? 'invert} (set! this going-down)
                else (inc! acc n)
          going-down
            λ (n)
              cond
                {n eq? 'invert} (set! this going-up)
                else (dec! acc n)
        going-up
  g2 10
  g2 'invert
  g2 3
  ;
  ;; which can be shortened to:
  define g3
    alet ([acc 0])
      alet-fsm
        going-up (n)  ; declare the initial state first.
          cond
            {n eq? 'invert} (state going-down)
            else (inc! acc n)
        going-down (n)
          cond
            {n eq? 'invert} (state going-up)
            else (dec! acc n)
  g3 10
  g3 'invert
  g3 3