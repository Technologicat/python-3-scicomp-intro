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
    format "  amb called, params ~a" params
  cond
    empty?(params)
      set! fail orig-fail
      fail()
    else
      let/cc cc
        set! fail
          λ ()
            cc (apply amb (map force (cdr params)))  ; forcing allows us to use "delay foo" as the cdr
        force (car params)  ; just in case (force on a value is harmless)

define assert(pred expr)
  displayln
    format "  assert ~a ~a" pred expr
  cond
    eq?(expr 'no-solution)
      displayln "    no solution"
      #f
    pred(expr)
      displayln "    ok"
      expr
    else
      displayln "    fail"
      fail()

module+ main
  define main()
    displayln "Hi! Demonstrating amb():"
    ;; We can't amb in a define, because the define would then be part of the continuation,
    ;; trying to re-define the same identifier when we fail().
    ;;
    ;; Instead, define first, then set!; to make fail() re-run only the set!.
    define foo 'not-initialized
    set! foo
      assert even? (amb 1 -1 2 3 5 7 8)
    displayln "Hi again!"
    cond
      foo
        displayln
          format
            "Found solution: ~a"
            foo
      else
        displayln "No more solutions found."
    fail()  ; jumps back to the amb, unless no more solutions
    ;;
    ;; This implementation is too simple to support the pythagorean triples example;
    ;; since there is no stack, multiple simultaneous "amb"s do not work. See choice.rkt.
  main()
