#lang sweet-exp racket

define unfold(proc init)
  let loop ([state init]
            [out empty])
    match (proc state)
      'end
        reverse out
      (cons value new-state)
        loop new-state (cons value out)

define step2(state) ; x0, x0 + 2, x0 + 4, ...
  match state
    (list k countdown)
      cond
        {countdown > 0}
          cons k (list {k + 2} {countdown - 1})
        else
          'end

define fibo(state)
  match state
    (list a b countdown)
      cond
        {countdown > 0}
          cons a (list b {a + b} {countdown - 1})
        else
          'end

define iter(state)  ; x0, f(x0), f(f(x0)), ...
  match state
    (list f x countdown)
      cond
        {countdown > 0}
          cons x (list f (f x) {countdown - 1})
        else
          'end

define zip-two(state)
  match state
    'end
      'end
    (list (cons a as) (cons b bs))
       cons
         list a b
         cond
           {(empty? as) or (empty? bs)}
             'end  ; this was the last value
           else
             list as bs

unfold step2 '(10 5)
unfold fibo '(1 1 20)
unfold iter (list (λ (x) {x * x}) 2 6)
unfold zip-two '((1 2 3 4) (5 6 7))
