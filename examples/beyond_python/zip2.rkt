#lang sweet-exp racket

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Utilities for mapping and zipping, while terminating on shortest or longest input.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Works for arbitary streams as input, but currently, explicitly constructs lists for output.

require racket/stream

provide zip zip< zip> map< map>

; simple variant: inputs must have equal length

; this doesn't work, because values() returns all outputs into one position
; (i.e. does not "unpack" into separate arguments in the Python sense)
;define zip(. args)
;  map list values(args)

; classical
;define zip(. args)
;  apply map list args

;equivalent
define zip (curry map list)

; terminate on shortest input, like Python's map
define map<(proc . input-streams)
  let iter ([acc empty]
            [streams input-streams])
        cond [(andmap not-empty? streams)
              define(firsts (map stream-first streams))
              define(rests  (map stream-rest  streams))
              define(newacc (cons (apply proc firsts) acc))
              iter(newacc rests)]
             [else (reverse acc)]

; terminate on longest input, generate fill-value for missing entries
define map>(proc #:fill-value [fill-value #f] . input-streams)
  let iter ([acc empty]
            [streams input-streams])
        cond [(ormap not-empty? streams)
               define(firsts apply(proc/fill stream-first streams #:fill-value fill-value))
               define(rests  apply(proc/fill stream-rest  streams #:fill-value empty))
               define(newacc (cons (apply proc firsts) acc))  ; we also proc fill-values here
               iter(newacc rests)]
             [else reverse(acc)]

define zip< (curry map< list)

; equivalent of Python's itertools.zip_longest
define zip>(#:fill-value [fill-value #f] . input-streams)
  apply map> list input-streams #:fill-value fill-value


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Helpers
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

define not-empty? (λ (x) (not (stream-empty? x)))

;; Process list of lists, gather results:
;; - For each non-empty list lst in lists, the result is proc(lst);
;;   proc/fill does not iterate over the elements of lst.
;; - For each empty list in lists, the result is fill-value.
;;
;; Works also for arbitrary streams.
;;
;; Example:
;;   apply proc/fill car lists
;; evaluates to (car(list0) ... car(listN)), but with fill-value as the car of any empty list.
;;
define proc/fill(proc #:fill-value [fill-value #f] . streams)
  for/list ([stream streams])
    cond [stream-empty?(stream) fill-value]
         [else proc(stream)]


;; Testing
;;
module+ main
  define a '(1 2 3)
  define b '(4 5 6)
  define c '(a b c)
  define d '(d e)
  define e '(f)
  ; variants of map
  map  (λ (x) {x * x}) a
  map< (λ (x) {x * x}) a
  map> (λ (x) {x * x}) a
  map  (λ (x y) {x * y}) a b
  map< (λ (x y) {x * y}) a b
  map> (λ (x y) {x * y}) a b
  ; variants of zip
  zip  a b
  zip< a b
  zip> a b
  zip< c d e
  zip> c d e
  zip> c d e #:fill-value '∅  ; 8709, "EMPTY SET"
