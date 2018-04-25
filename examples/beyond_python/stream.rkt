#lang sweet-exp racket

;;; Infinite streams. This version supports Racket's match for pattern matching.
;;;
;;; A stream is a pair, where the car is an element of the stream, and the cdr
;;; is a promise to compute the rest of the stream.
;;;
;;; Accessing the cdr of the stream forces the promise, generating one more element
;;; of the stream, and a new promise to compute more.
;;;
;;; Take this into account when sconsing a stream! The tail should be a procedure,
;;; which sconses the next element and a procedure to continue computing the stream.
;;;
;;; See SICP 2nd ed., sec. 3.5.1.
;;;   https://mitpress.mit.edu/sicp/full-text/book/book-Z-H-24.html#%_sec_3.5.1

;;; This is just for teaching purposes; Racket already provides a stream abstraction,
;;; which can do this and much more.
;;; 
;;;   https://docs.racket-lang.org/reference/streams.html
;;;
;;; For further reading, see also:
;;;
;;;   https://sites.ualberta.ca/~jhoover/325/CourseNotes/section/Streams.htm
;;;   https://docs.racket-lang.org/srfi/srfi-std/srfi-41/srfi-41.html

require syntax/parse/define

(provide sempty sempty?
         s? scons scar scdr sref
         smap sfilter
         for/s for/s/list s->list
         sadd smul)

define sempty  ; needs to be infinite to represent empty "rest" term in destructuring
  scons 'none sempty
define sempty?(s)
  eq? (scar s) 'none

;; We must delay the evaluation of b already when scons is called, so in an eager language
;; scons must be a syntax. See Felleisen (1991):
;;   http://www.ccis.northeastern.edu/racket/pubs/scp91-felleisen.ps.gz
;;   https://www2.ccs.neu.edu/racket/pubs/
;define-syntax-parser scons
;  (_ a b) #'(list 'stream a (delay b))

require (for-syntax syntax/parse)

;; data abstraction
;; https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-13.html#%_chap_2
;;
define-match-expander  ; let's support Racket's match, too
  scons
  λ (stx)  ; in a match pattern - destructuring bind
    syntax-parse stx
      (_ a:id rest:id) #'(? s? (app s-destructure-one a rest))
      (_ a:id b:id rest:id) #'(? s? (app s-destructure-two a b rest))
      (_ a:id b:id c:id rest:id) #'(? s? (app s-destructure-three a b c rest))
  λ (stx)  ; in an expression context (i.e. anywhere else) - constructor
    syntax-parse stx
      (_ a:expr b:expr) #'(list 'stream a (delay b))
define s?(s) {(pair? s) and (eq? (car s) 'stream)}
define s-current-element(s) (cadr s)
define s-current-promise(s) (caddr s)

define scar(s)
  cond
    (not (s? s))
      raise-argument-error 'scar "s?" s
    else
      s-current-element s

define scdr(s)
  cond
    (not (s? s))
      raise-argument-error 'scdr "s?" s
    else
      define t (force (s-current-promise s))
      cond
        (s? t)  ; the once-forced tail is still a stream: more terms exist
          t
        else    ; t is the last element of s, not a stream; but the scdr of a stream must be a stream.
          scons t sempty  ; (needed, since we don't demand the user to start sconsing from sempty)

define sref(s n)
  cond
    (not (s? s))
      raise-argument-error 'sref "s?" s
    {{n < 0} or not(integer?(n))}
      raise-argument-error 'sref "and/c integer? (>=/c n 0)" n
    {n = 0}
      scar s
    else
      sref (scdr s) {n - 1}

define s-destructure-one(s)
  let ([a (scar s)]
       [t (scdr s)])
    values a t

define s-destructure-two(s)
  let*-values ([(a t) (s-destructure-one s)]
               [(b t) (s-destructure-one t)])
    values a b t

define s-destructure-three(s)
  let*-values ([(a t) (s-destructure-one s)]
               [(b t) (s-destructure-one t)]
               [(c t) (s-destructure-one t)])
    values a b c t

;; Map for a single input stream.
;define smap(proc s)
;  cond
;    sempty?(s)
;      empty
;    else
;      scons proc(scar(s)) smap(proc scdr(s))

;; Map for multiple input streams.
;; This requires all input streams to be the same length (countably infinite also ok).
define smap(proc . streams)
  cond
    sempty?(car(streams))  ; same length, sufficient to check the first one
      sempty
    else
      scons
        apply proc (map scar streams)
        apply smap proc (map scdr streams)

define sfilter(pred s)
  cond
    sempty?(s)
      sempty
    pred(scar(s))
      scons (scar s) (sfilter pred (scdr s))
    else
      sfilter pred (scdr s)

;; A rudimentary for-each for streams.
;;
;; The keyword argument "nterms" stops evaluation after n terms.
;; After stopping, the cdr of the stream is returned.
;;
define for/s(proc s #:nterms [nterms -1])
  cond
    sempty?(s)
      sempty
    {nterms = 0}
      s
    else
      proc scar(s)
      for/s proc scdr(s) #:nterms {nterms - 1}

;; Like for/s, but gather results to a list, and return the list.
;;
define for/s/list(proc s #:nterms [nterms -1])
  define out empty
  define proc-and-store(x) (set! out (cons proc(x) out))
  for/s proc-and-store s #:nterms nterms
  reverse out

;; Like for/s/list, but just collect the elements of s.
;;
;; Racket already provides stream->list for the stream abstraction in the
;; standard library, so we use a different name in order not to mask that
;; if the user plain requires this module.
;;
define s->list(s #:nterms [nterms -1])
  define pass-through(x) x
  for/s/list pass-through s #:nterms nterms

;; Add two streams.
define sadd(s1 s2)
  smap + s1 s2

;; Multiply a stream by a constant.
define smul(s c)
  smap (λ (x) {c * x}) s
;  smap (curry * c) s  ; equivalent

;; Usage examples
;;
module+ main
  define divisible(n k)
    {(remainder n k) = 0}
  ;; Implicit definitions like this are ok, as long as the already-generated part
  ;; of the stream is sufficient to generate the next value. Racket memoizes the
  ;; results from already forced promises, so there is no additional runtime cost.
  letrec
    \\  ; GROUP, https://srfi.schemers.org/srfi-110/srfi-110.html
      ones
        scons 1 ones
      naturals
        scons 0 (sadd ones naturals)
      powers-of-2
        scons 1 (smul powers-of-2 2)
      multiples-of-7
        sfilter (λ (x) (divisible x 7)) naturals
      fibonacci
        scons 0 (scons 1 (sadd (scdr fibonacci) fibonacci))
      repeat  ; a, f(a), f(f(a)), ...
        λ (f a)
          scons a (repeat f (f a))
    ;
    displayln "ones"
    for/s displayln ones #:nterms 10
    ;
    displayln "naturals"
    for/s displayln naturals #:nterms 10
    ;
    displayln "powers of 2"
    for/s displayln powers-of-2 #:nterms 10
    ;
    displayln "multiples of 7"
    for/s displayln multiples-of-7 #:nterms 10
    ;
    displayln "Fibonacci's numbers"
    for/s displayln fibonacci #:nterms 10
    ;
    displayln "Repeated function application"
    for/s displayln (repeat (λ (x) (* x x)) 2) #:nterms 5
    ;
    ;; Converting part of a stream into a list
    define lst1
      for/s/list (λ (x) x) multiples-of-7 #:nterms 10
    define lst2
      s->list multiples-of-7 #:nterms 10
    ;
    displayln "Reading further into a stream: 2**200"
    displayln (sref powers-of-2 200)
    ;
    ;; whyfp pp. 11 fw.
    ;
    ;; Let's consider what we can do with this, *without* changing to a more accurate formula...
    define easydiff(f x h)
      {{(f {x + h}) - (f x)} / h}
    ;
    define halve(x) {x / 2}
    define differentiate(h0 f x)
      smap (curry easydiff f x) (repeat halve h0)
    ;
    define within(eps s)
      match s
        (scons a b rest)
          cond
            {(abs {a - b}) < eps}
              b
            else
              within eps (scons b rest)  ; b already computed; more efficient than (scdr s)
    define differentiate-with-tol(h0 f x eps)
      within eps (differentiate h0 f x)
    ;
    displayln differentiate-with-tol(0.1 sin {pi / 2} 1e-8)
    ;
    ;; - n must be the asymptotic order of the error term to eliminate
    ;; - the sequence must be based on halving h at each step
    define eliminate-error(n s)
      match s
        (scons a b rest)
          scons {{{b * (expt 2 n)} - a} / (expt 2 {n - 1})} (eliminate-error n (scons b rest))
    define order(s)
      match s
        (scons a b c rest)
          round (log {(abs {{a - c} / {b - c}}) - 1} 2)
    define improve(s)
      eliminate-error (order s) s
    define better-differentiate-with-tol(h0 f x eps)
      within eps (improve (differentiate h0 f x))
    ;
    displayln better-differentiate-with-tol(0.1 sin {pi / 2} 1e-8)
    ;
    define ssecond(s) (sref s 1)
    define super-improve(s)
      smap ssecond (repeat improve s)
    define best-differentiate-with-tol(h0 f x eps)
      within eps (super-improve (differentiate h0 f x))
    ;
    displayln best-differentiate-with-tol(0.1 sin {pi / 2} 1e-8)

;; test the pattern matching features
module+ main
  define tmp2 (scons 1 2)
  match tmp2
    (scons a rest)
      displayln (format "~a ~a" a rest)
  match tmp2
    (scons a b rest)
      displayln (format "~a ~a ~a" a b rest)
  match tmp2
    (scons a b c rest)
      displayln (format "~a ~a ~a ~a" a b c rest)
  ;
  define tmp3 (scons 1 (scons 2 3))
  match tmp3
    (scons a rest)
      displayln (format "~a ~a" a rest)
  match tmp3
    (scons a b rest)
      displayln (format "~a ~a ~a" a b rest)
  match tmp3
    (scons a b c rest)
      displayln (format "~a ~a ~a ~a" a b c rest)
