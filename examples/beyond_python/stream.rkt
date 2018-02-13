#lang sweet-exp racket

;;; Infinite streams.
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
         scons scar scdr sref
         smap sfilter
         for/s for/s/list s->list
         sadd smul)

define sempty empty
define sempty? empty?

;; We must delay the evaluation of b already when scons is called, so in an eager language
;; scons must be a syntax. See Felleisen (1991):
;;   http://www.ccis.northeastern.edu/racket/pubs/scp91-felleisen.ps.gz
;;   https://www2.ccs.neu.edu/racket/pubs/
define-syntax-parser scons
  (_ a b) #'(cons a (delay b))

define scar(s) (car s)
define scdr(s) (force (cdr s))

define sref(s n)
  cond
    {{n < 0} or not(integer?(n))}
      raise-argument-error 'sref "and/c integer? (>=/c n 0)" n
    {n = 0}
      scar s
    else
      sref (scdr s) {n - 1}

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
        apply smap (cons proc (map scdr streams))

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
    ;; Converting part of a stream into a list
    define lst1
      for/s/list (λ (x) x) multiples-of-7 #:nterms 10
    define lst2
      s->list multiples-of-7 #:nterms 10
    ;
    displayln "Reading further into a stream: 2**200"
    displayln (sref powers-of-2 200)
