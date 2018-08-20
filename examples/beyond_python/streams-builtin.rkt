#lang sweet-exp racket

;; Port of stream.rkt to Racket's builtin streams.
;;
;; We provide some capabilities that the standard library doesn't already.
;; Notably, we enable match for stream-cons (destructuring up to the first three elements).

provide stream-cons stream-take make-recursive-streams-proc stream-zip stream-add stream-mul

require (rename-in racket/stream [stream-cons %stream-cons])
require (for-syntax syntax/parse)

define-match-expander  ; let's support Racket's match, too
  stream-cons
  λ (stx)  ; in a match pattern - destructuring bind
    syntax-parse stx
      (_ a:id rest:id) #'(? stream? (app destructure1 a rest))
      (_ a:id b:id rest:id) #'(? stream? (app destructure2 a b rest))
      (_ a:id b:id c:id rest:id) #'(? stream? (app destructure3 a b c rest))
  λ (stx)  ; in an expression context (i.e. anywhere else) - business as usual
    syntax-parse stx
      (_ args ...) #'(%stream-cons args ...)

define destructure1(s)
  let ([a (stream-first s)]
       [t (stream-rest s)])
    values a t

define destructure2(s)
  let*-values ([(a t) (destructure1 s)]
               [(b u) (destructure1 t)])
    values a b u

define destructure3(s)
  let*-values ([(a t) (destructure1 s)]
               [(b u) (destructure1 t)]
               [(c v) (destructure1 u)])
    values a b c v

define stream-take(s n)
  for/list ([_ (in-range n)]  ; eventually stop evaluation
            [x (in-stream s)])
    x

;; Return a procedure that, given any number of streams, constructs a new stream:
;;
;;   - Apply the procedure f to the first elements of the input streams (f must take as many arguments
;;     as there are input streams); its return value is then the first element of the new stream.
;;
;;   - Then recurse into the tail.
;;
;; This is useful for defining stream utilities such as stream-zip and stream-add.
define make-recursive-streams-proc(f)
  define streams-apply-and-recurse(. ss)  ; TODO: shorter but descriptive name for debug prints
    stream-cons
      apply f (map stream-first ss)
      apply streams-apply-and-recurse (map stream-rest ss)
  streams-apply-and-recurse
define stream-zip (make-recursive-streams-proc list)  ; zip streams
define stream-add (make-recursive-streams-proc +)     ; add streams elementwise

;; Multiply a stream by a constant.
define stream-mul(s c)
  stream-map
    λ (x) {c * x}
    s

module+ main
  define divisible(n k) {(remainder n k) = 0}
  define ones
    stream-cons 1 ones
  define naturals
    stream-cons
      0
      stream-add naturals ones
  define multiples-of-7
    stream-filter
      λ (x) (divisible x 7)
      naturals
  define powers-of-2
    stream-cons
      1
      stream-mul powers-of-2 2
  define fibo
    stream*
      1
      1
      stream-add
        fibo
        stream-rest fibo
  define repeat(f x)  ; x, f(x), f(f(x)), ...
    stream-cons
      x
      repeat f (f x)
  ;
  for ([s (list
             ones
             naturals
             multiples-of-7
             powers-of-2
             fibo
             (repeat (λ (x) (* x x)) 2)
             (stream-zip naturals powers-of-2))])
    displayln (stream-take s 5)
  ;
  ;; whyfp pp. 11 fw.
  ;
  ;; Let's consider what we can do with this, *without* changing to a more accurate formula...
  define easydiff(f x h)
    {{(f {x + h}) - (f x)} / h}
  ;
  define halve(x) {x / 2}
  define differentiate(h0 f x)
    stream-map (curry easydiff f x) (repeat halve h0)
  ;
  define within(eps s)
    match s
      (stream-cons a b rest)
        cond
          {(abs {a - b}) < eps}
            b
          else
            within eps (stream-cons b rest)  ; b already computed; more efficient than (scdr s)
  define differentiate-with-tol(h0 f x eps)
    within eps (differentiate h0 f x)
  ;
  displayln differentiate-with-tol(0.1 sin {pi / 2} 1e-8)
  ;
  ;; - n must be the asymptotic order of the error term to eliminate
  ;; - the sequence must be based on halving h at each step
  define eliminate-error(n s)
    match s
      (stream-cons a b rest)
        stream-cons
          {{{b * (expt 2 n)} - a} / (expt 2 {n - 1})}
          eliminate-error n (stream-cons b rest)
  define order(s)
    match s
      (stream-cons a b c rest)
        round (log {(abs {{a - c} / {b - c}}) - 1} 2)
  define improve(s)
    eliminate-error (order s) s
  define better-differentiate-with-tol(h0 f x eps)
    within eps (improve (differentiate h0 f x))
  ;
  displayln better-differentiate-with-tol(0.1 sin {pi / 2} 1e-8)
  ;
  define ssecond(s) (stream-ref s 1)
  define super-improve(s)
    stream-map ssecond (repeat improve s)
  define best-differentiate-with-tol(h0 f x eps)
    within eps (super-improve (differentiate h0 f x))
  ;
  displayln best-differentiate-with-tol(0.1 sin {pi / 2} 1e-8)
