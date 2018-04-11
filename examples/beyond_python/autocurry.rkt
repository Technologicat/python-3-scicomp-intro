#lang sweet-exp racket

;; Now available as a #lang; moved to:
;;   https://github.com/Technologicat/spicy
;;
;; This old version will remain available here.

;; An experiment in automatic currying for Racket.
;;
;; In general, this sort of thing cannot be made to play well with variadic functions,
;; so this is mainly useful for teaching purposes.
;;
;; See e.g.
;;   https://stackoverflow.com/questions/11218905/is-it-possible-to-implement-auto-currying
;;      -to-the-lisp-family-languages
;;   http://paqmind.com/blog/currying-in-lisp/
;;
;; Inspiration:
;;   http://www.cse.chalmers.se/~rjmh/Papers/whyfp.html
;;
;; TODO: Does not currently work with kwargs. Like Racket's original, also our modified curry()
;; supports them (if provided immediately in the first call), but spice() needs to pass them through,
;; and #%spicy-app also needs minor tuning to do the right thing in the various different cases.

provide
  all-from-out 'spicy  ; for use from other modules

module spicy racket
  provide
    except-out
      all-from-out racket
      #%app
    rename-out
      #%spicy-app #%app
    curry
    ; TODO: curryr
    compose
  ;
  require
    rename-in
      racket
      [compose compose-impl]
  ;
  require racket/performance-hint
  require syntax/parse/define
  require "values-listify.rkt"
  ;
  ;; Things such as (displayln 'foo) work because we spice the bare proc first,
  ;; and only then apply any arguments to it. The arity of displayln includes 1,
  ;; so the curried version gets called immediately even if there is just one argument.
  ;;
  ;; Obviously, if the first set of args already has an arity that the function accepts,
  ;; then it is not possible to add more args by currying. For some variadic functions (esp. + *),
  ;; this means that all args should be passed in one call, in the usual rackety manner.
  ;;
  ;; There is a slight difference in behavior when compared to Racket's curry:
  ;;
  ;;   - Racket's curry treats the first call to the curried proc specially: only n = max-arity
  ;;     arguments trigger a call to the original procedure. But during second and further calls,
  ;;     *any acceptable arity* triggers a call.
  ;;
  ;;   - Autocurry always enters the second operation mode immediately: any acceptable arity
  ;;     will trigger a call. This makes procedures with optional args behave more consistently.
  ;;
  ;;     (Consider especially the case of just one arg, which is optional: how to tell curry to use
  ;;      the default value? Racket's curry just returns a curried procedure, because max-arity was
  ;;      not reached yet; the returned procedure must be called again to actually trigger a call
  ;;      into the original procedure. The second call triggers, because the mode has changed.)
  ;;
  define-syntax-parser #%spicy-app
    #:literals (curry)
    (_ curry proc maybe-args ...)  ; allow explicit curry() without spicing it
      #'(#%app curry proc maybe-args ...)
    ;
    ;; Simpler machinery; works like Racket's curry.
    ;; Requires the user to make an extra call if using defaults for optional args.
;    (_ proc)
;      #'(#%app (spice proc))
;    (_ proc arg ...)
;      #'((#%spicy-app proc) arg ...)
    ;
    ;; Maybe-easier-to-use approach.
    (_ proc)
      #'(let ([spiced ((spice proc))])  ; if proc has max-arity 0, calls; else returns curried proc
           ;(displayln (format "DEBUG: spiced is: ~a" spiced))
           (cond
             ([eq? object-name(spiced) 'curried]
                ;(displayln "DEBUG: calling spiced proc")
                (spiced))  ; Change the operation mode of the curried procedure
                           ; to call as soon as any acceptable arity is provided.
             (else spiced)))  ; Original proc already called, just return results.
    (_ proc arg ...+)
      #'(((spice proc)) arg ...)
  ;
  ;; curry proc if not yet curried, else return proc as-is.
  define-inline spice(proc)
    cond
      (not (eq? object-name(proc) 'curried))  ; TODO: more robust way to detect?
        ;displayln (format "DEBUG: spicing: ~a" object-name(proc))
        curry proc
      else
        proc
  ;
  ;; Most higher-order functions we don't need to touch, but those that combine user-given functions
  ;; (such as compose() here) may need to spice() their arguments.
  ;;
  ;; Those are not in operator position, and hence #%spicy-app won't automatically apply to them.
  ;;
  define compose(. args)
    apply compose-impl (map spice args)
  ;
  ;; Curry, modified to support more than max-arity args.
  ;;
  ;; - When curry() is called with just proc (no args for it), it just sets up currying,
  ;;   and returns the curried procedure.
  ;;
  ;;   - The first call into the curried procedure tests for n >= max-arity, and if so,
  ;;     calls the original proc immediately. (For n > max-arity, see details below.)
  ;;
  ;;     NOTE: if max-arity is 0, this will already trigger a call into the original procedure!
  ;;
  ;;   - But if n < max-arity, that call just changes the operation mode of the curried procedure.
  ;;     After the mode change, *any acceptable arity* (not just max-arity) will trigger a call
  ;;     to the original procedure.
  ;;
  ;; - If curry() is called with proc and args, those args are used to immediately perform
  ;;   the first call into the curried procedure. This is also the only way to pass in kwargs.
  ;;
  ;; If the curried procedure is called with n > max-arity arguments:
  ;;
  ;; - The arglist is split into two parts.
  ;; - The original procedure is called with the first max-arity args.
  ;; - What happens next depends on the return value:
  ;;   - If it is a single value, which contains another curried procedure,
  ;;     that procedure is applied to the remaining arguments.
  ;;   - Otherwise any extra args are passed through on the right.
  ;;     The return value(s) and the extra args are combined into a single multiple-values object.
  ;;
  ;; TODO: generalize passthrough to work correctly with curryr
  ;;
  ;; Based on make-curry in Racket 6.10.1 [3m], collects/racket/function.rkt
  ;;
  ;; The implementation is deliberately kept as close to the original as possible, to make this
  ;; (at least nearly) a drop-in replacement for Racket's curry. The special-casing for max-arity 0
  ;; is done in #%spicy-app instead.
  ;
  (define (make-curry right?)
    ;; The real code is here
    (define (curry* f args kws kvs)
      (unless (procedure? f)
        (raise-argument-error (if right? 'curryr 'curry) "procedure?" f))
      (let* ([arity (procedure-arity f)]
             [max-arity (cond [(integer? arity) arity]
                              [(arity-at-least? arity) #f]
                              [(ormap arity-at-least? arity) #f]
                              [else (apply max arity)])]
             [n (length args)])
        ;(displayln
        ;  (format "DEBUG: curry: ~a: arity ~a, max ~a, n ~a, args ~a" f arity max-arity n args))
        (define (call-with-extra-args args)
           (let-values ([(now-args later-args) (split-at args max-arity)])
               ;(displayln (format "DEBUG: now: ~a, later: ~a" now-args later-args))
               ;(displayln (format "DEBUG: >-max-arity CALL: ~a" f))
               (define now-result (values->list (if (null? kws)
                                                    (apply f now-args)
                                                    (keyword-apply f kws kvs now-args))))
               ;; If the now-result is a single value, which contains a curried proc,
               ;; call it with the extra args, to better support point-free style.
               (define g (car now-result))
               (cond
                 ([and (empty? (cdr now-result))
                       (procedure? g)
                       (eq? (object-name g) 'curried)]
                   (apply g later-args))
                 ;; Otherwise pass any extra args through on the right.
                 (else
                   (list->values (append now-result later-args))))))
        (define (loop args n)
          ;(displayln
          ;  (format "DEBUG: loop: ~a: arity ~a, max ~a, n ~a, args ~a" f arity max-arity n args))
          (cond
            ([procedure-arity-includes? f n]
             ;(displayln (format "DEBUG: arity-includes CALL: ~a" f))
             (if (null? kws) (apply f args) (keyword-apply f kws kvs args)))
            ([and max-arity {n > max-arity}]  ; original just raises an error in this case
              (call-with-extra-args args))
            (else
              (letrec [(curried
                        (case-lambda
                          [() curried] ; return itself on zero arguments
                          [more (loop (if right?
                                          (append more args) (append args more))
                                      (+ n (length more)))]))]
                curried))))
        ;; take at least one step if we can continue (there is a higher arity)
        (cond
          ; handle >= max-arity args, when given in the first call (before loop() is called).
          ([equal? n max-arity]
            ;(displayln (format "DEBUG: exact-arity CALL: ~a" f))
            (if (null? kws) (apply f args) (keyword-apply f kws kvs args)))
          ([and max-arity {n > max-arity}]
            (call-with-extra-args args))
          (else
            (letrec ([curried
                      (lambda more
                        (let ([args (if right?
                                        (append more args) (append args more))])
                          (loop args (+ n (length more)))))])
              ;(displayln (format "DEBUG: letrec: ~a, args: ~a" f args))
              curried)))))
    ;; curry is itself curried -- if we get args then they're the first step
    (define curry
      (case-lambda [(f) (define (curried . args) (curry* f args '() '()))
                        curried]
                   [(f . args) (curry* f args '() '())]))
    (make-keyword-procedure (lambda (kws kvs f . args) (curry* f args kws kvs))
                            curry))
  ;
  (define curry  (make-curry #f))
  ;(define curryr (make-curry #t))  ; TODO: curryr

;; load it
require 'spicy

;; test it
module+ main
  define f(x) {x * x}
  define g(x y) {{2 * x} + {3 * y}}
  f(4)     ; single-arg functions behave as usual
  g(2 5)   ; classical call with several arguments - behaves like usual
  g 2 5    ; in sweet-exp, this is also a call with several arguments
  g(2)(5)  ; auto-curried - this now works, too.
  ;
  ;; any extra args > max arity are passed through (on the right):
  let-values ([(a b) g(2 5 8)])
    displayln a  ; result of g(2 5)
    displayln b  ; 8
  ;
  ;; The automatic passthrough can be utilized for Haskell-y idioms like this:
  ;;   - foldr calls proc(elt acc), so proc must accept 2 arguments
  ;;   - but f doesn't; its signature is 1->1. The extra arg is passed through on the right.
  ;;   - signature of cons is 2->1
  ;;   - foldr uses the output of proc as the new value of acc
  define mymap1(f lst)
    foldr (compose cons f) empty lst
  mymap1 f '(1 2 3)
  ;
  ;; We may also use point-free style, omitting the lst:
  define mymap2(f)
    foldr (compose cons f) empty
  (mymap2 f) '(1 2 3)  ; invoke (mymap2 f) first to get the "f-mapper" function for our "f"
  ;
  ;; This also works, because in our curry(), a curried proc intermediate result
  ;; means that the procedure is applied to the remaining arguments.
  ;;
  ;; The difference to the "g 2 5" example is that here, the arity of mymap2 is just 1.
  ;;
  mymap2 f '(1 2 3)
  ;
  define thunk()  ; test 0-arity function
    displayln "hello"
  thunk()
  ;
  ;; Test optional args
  define f-with-optional-arg([x 42])
    displayln x
  procedure-arity f-with-optional-arg  ; '(0 1)
  f-with-optional-arg(23)
  f-with-optional-arg()  ; 0 is a valid arity for this proc; calls immediately
  ;
  ;; OTOH, we do lose something:
  + 1  ; computes result since 1 is a valid arity - can't curry
  ;
  ;; to work around, make operations with a fixed max-arity:
  define add(a b) (+ a b)
  define sub(a b) (- a b)
  define mul(a b) (* a b)
  define div(a b) (/ a b)
  ;; (expt is already binary-only, no need)
  ;
  ;; Now we can curry addition, allowing a point-free definition e.g. of the classic "one-adder":
  define add1
    add 1
  ;
  ;; Of course, the trivial lispy way to create a one-adder is:
  define add1-variant2(x)
    + 1 x
  ;; which is equivalent to
  define add1-variant3
    λ (x) (+ 1 x)
  ;
  ;; The almost point-free SRFI-26 way:
  ;; https://srfi.schemers.org/srfi-26/srfi-26.html
  require
    only-in srfi/26
      cut
      cute
  define add1-variant4
    cut + 1 <>
  ;
  add1 42
  add1-variant2 42
  add1-variant3 42
  add1-variant4 42
