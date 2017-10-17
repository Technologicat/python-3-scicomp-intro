#!/usr/bin/env racket
#lang sweet-exp r5rs

;; Demonstrate tail calls. Code examples from:
;;
;; https://en.wikipedia.org/wiki/Tail_call

;; Unlike the other examples, this is written in R5RS scheme
;; (but still converted to t-expressions).


;; a simple routine to duplicate a list:

define simple-duplicate(ls)
  if (not null?(ls))
    cons (car ls)
         simple-duplicate (cdr ls)
    '()

;; original in s-expression syntax:
;(define (simple-duplicate ls)
;  (if (not (null? ls))
;    (cons (car ls)
;          (simple-duplicate (cdr ls)))
;    '()))


;; tail call version

define duplicate(ls)
  let ([head (list 1)])           ; the 1 is a sentinel to simplify the code
    let dup ([ls ls] [end head])  ; named let, R5RS sec. 4.2.4 Iteration
      if (not null?(ls))
        begin 
          set-cdr! end (list (car ls))
          dup (cdr ls) (cdr end)
    cdr head

;(define (duplicate ls)
;  (let ((head (list 1)))
;    (let dup ((ls ls) (end head))
;      (if (not (null? ls))
;        (begin 
;          (set-cdr! end (list (car ls)))
;          (dup (cdr ls) (cdr end)))))
;    (cdr head)))


;; loop version

define duplicate-by-loop(ls)
  let ([head (list 1)])
    do ([end head (cdr end)]         ; ((var1 init1 step1)  R5RS sec. 4.2.4 Iteration
        [ls  ls   (cdr ls )])        ;  ...)
       null?(ls) (cdr head)          ; (test expr ...)    if true, return result of last expr, else..
       set-cdr! end (list (car ls))  ; ..perform this command (for its side effects) and loop

;(define (duplicate-by-loop ls)
;  (let ((head (list 1)))
;    (do ((end head (cdr end))
;         (ls  ls   (cdr ls )))
;        ((null? ls) (cdr head))
;      (set-cdr! end (list (car ls))))))

define L '(1 2 3)
display L

define L1 simple-duplicate(L)
display L1

define L2 duplicate(L)
display L2

define L3 duplicate-by-loop(L)
display L3
