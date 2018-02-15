#lang sweet-exp racket

;; A very minimal purely procedural choice operator (no macros).
;; See also choice.rkt.
;;
;; This one adapted from:
;; http://wiki.c2.com/?ContinuationsAreGotos

provide amb assert fail

define fail()
  'no-solution
define orig-fail fail

define amb(. params)
  displayln
    format "amb, params ~a" params
  cond
    empty?(params)
      set! fail orig-fail
      fail()
    else
      let/cc cc
        set! fail
          λ ()
            cc (apply amb (cdr params))
        car params

define assert(pred expr)
  displayln
    format "assert ~a ~a" pred expr
  cond
    eq?(expr 'no-solution)
      displayln "  no solution"
      #f
    pred(expr)
      displayln "  ok"
      expr
    else
      displayln "  fail"
      fail()

module+ main
  ;; We can't amb in a define, because the define would then be part of the continuation,
  ;; trying to re-define the same identifier when we fail().
  ;;
  ;; Instead, define first, then set!; to make fail() re-run only the set!.
  define foo 'not-initialized
  set! foo
    assert even? (amb 1 -1 2 3 5 7 8)
  foo
  fail()
  foo
  fail()
  foo
