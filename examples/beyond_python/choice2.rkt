#lang sweet-exp racket

;; Another version of choice.rkt, where choice() is now a procedure.

;; Non-deterministic evaluation - a simple example of building declarative programming onto Racket.
;;
;; We use a very simple exhaustive search; no attempt at "truth maintenance".
;; For a more in-depth discussion on this topic, see the "amb" evaluator in SICP.
;;
;; This example is based on:
;;   David Liu (2014): Continuations and Backtracking in Racket:
;;   http://www.cs.toronto.edu/~david/courses/csc324_w15/extra/choice.html
;;
;; For a more serious attempt at this, the Racket repository provides Racklog:
;;   https://docs.racket-lang.org/racklog/index.html

require syntax/parse/define

provide choice next clear all query all-query assert

;; To encapsulate the internal state, we want to represent the stack as an object.
;;
;; We could use a struct:
;;   https://docs.racket-lang.org/guide/define-struct.html
;; with prop:procedure as a dispatcher, or
;;   https://docs.racket-lang.org/guide/classes.html
;; to make a class, but a closure is enough for our purposes here.
;;
;; A koan about objects and closures.
;; http://people.csail.mit.edu/gregs/ll1-discuss-archive-html/msg03277.html
;;
define make-stack()
  define s empty  ; instance variable
  ;
  define push(item)
    set! s cons(item s)
  ;
  define next()
    cond
      empty?(s)
        #f
      else
        let ([current-choice car(s)])
          set! s cdr(s)
          current-choice()
  ;
  define clear()
    set! s empty
  ;
  define stack-length()
    length s
  ;
  define is-empty?()
    empty?(s)
  ; dispatcher - this is returned by make-stack()
  λ (op)
    case op
      [(push) push]
      [(next) next]
      [(clear) clear]
      [(length) stack-length]
      [(is-empty?) is-empty?]

define the-stack make-stack()  ; singleton instance (TODO: needs thread-local storage)
define push the-stack('push)   ; grab the instance methods
define next the-stack('next)
define clear the-stack('clear)
define stack-length the-stack('length)
define is-stack-empty? the-stack('is-empty?)

;; equivalent to
;;
;; define-syntax choice
;;   syntax-parser
;;     ...
;;
;; which is further equivalent to
;;
;; define-syntax choice(stx)
;;   syntax-parse stx
;;     ...
;;
;; In the other variants, the "stx" parameter of the last variant is available as "this-stx".
;;
;define-syntax-parser choice
;  [_ expr0]
;    #'expr0
;  [_ expr0 expr ...+]
;    syntax
;      let/cc cc
;        displayln
;          format
;            "items already in queue: ~a; expr0: ~a"
;            stack-length()
;            expr0
;        push (λ () (cc (choice expr ...)))
;        expr0
;; choice does not work as a procedure in all use cases, since exprs must be evaluated lazily.
define choice(expr0 . exprs)
  cond
    empty?(exprs)
      expr0
    else
      let/cc cc
;        displayln
;          format
;            "items already in queue: ~a; expr0: ~a; exprs ~a"
;            stack-length()
;            expr0
;            exprs
        push (λ () (cc (apply choice (map force exprs))))
        force expr0

define query(pred expr)
  cond
    pred(expr)
      expr
    else
      next()

define assert(pred)  ; sometimes more convenient than query.
  cond
    pred
      #t
    else
      next()

define-syntax-parser all
  [_ choice-expr]
    #'(all-query (λ (x) #t) choice-expr)

;; query doesn't compose properly into all, so we implement their combination,
;; which can reduce into the basic "all" when needed.
;;
;; The issue is that
;;   all query ...
;; gets #f as the last item if the last combination does not match pred,
;; since the return value from the final next() (returning #f when stack empty)
;; is then left standing as the result of query().
define-syntax-parser all-query
  [_ pred choice-expr]
    syntax
      let ([result empty])
        cond
          not(is-stack-empty?())
            ;; If the stack is not empty when entering the all-query,
            ;; it likely still contains a continuation from a previous search
            ;; that will make the calling code fail in very weird ways.
            ;;
            ;; Explicit is better than implicit - we leave it to the user
            ;; to make sure the stack is empty before attempting an all-query.
            ;;
            ;; (all-query itself always leaves the stack empty; only manual calls
            ;;  to next() can leave items there, if all choices have not been exhausted.)
            error "all-query: expected stack to be empty"
        define iter(expr)
          cond
            pred(expr)
              set! result cons(expr result)
          next()  ; until stack empty, jumps...
          reverse(result)
        iter(choice-expr)  ; ...back here (since the choice operators appear in choice-expr!)


;; Note: Racket already has generators in the standard library, so we don't need this.
;;
;; Some care needs to be taken when naming the return value from this one:
;; - define g generator(...) will trigger a re-definition error at runtime,
;;   because the continuation attempts to resume defining g.
;; - Instead, this works:
;;     define g '()
;;     set! g generator(...)
;;   since the continuation now only "set!"s g.
;; - We could encapsulate that into a "define-generator" syntax, if we wanted.
define generator(lst)
  cond
    empty?(lst)
      #f
    else
      choice car(lst) (delay generator(cdr(lst)))


;; This doesn't work with the procedure version of choice().
;;
;; http://www.cs.toronto.edu/~david/courses/csc324_w15/extra/choice.html
;; example by Gary Baumgartner
(define (formula depth)
  (if (equal? depth 0)
      (list (choice 'P 'Q) (choice 'x 'y))
      (let ([d (- depth 1)])
        (choice (list '¬ (formula d))
                (list (formula d) '∧ (formula d))
                (list (formula d) '∨ (formula d))))))

module+ main
  choice 1 2 3  ; returns 1
  next()  ; 2
  next()  ; 3
  next()  ; #f
  ;
  {choice(1 2) + choice(30 40)}
  next()
  next()
  next()
  next()
  ;
  all choice(1 2 3 4)
  ;
  all {choice(3 10 6) + choice(100 200)}
  ;
  all query(even? {choice(4 5) + choice(11 14)})
  ;
  all-query(even? {choice(4 5) + choice(11 14)})
  ;
  generator '(1 2 3 4)
  next()
  next()
  next()
  next()
  ;
  define g '()
  set! g generator('(1 2 3 4))
  g
  next()
  g
  next()
  g
  next()
  g
  next()
  g
  ;
;  all formula(1)
  ;
  ;; Find a Pythagorean triple.
  ;; http://matt.might.net/articles/programming-with-continuations-
  ;;        -exceptions-backtracking-search-threads-generators-coroutines/
  let ([a (choice 1 2 3 4 5 6 7)]
       [b (choice 1 2 3 4 5 6 7)]
       [c (choice 1 2 3 4 5 6 7)])
    assert (= (* c c) (+ (* a a) (* b b)))
    displayln (list a b c)
    assert (< b a)
    displayln (list a b c)
