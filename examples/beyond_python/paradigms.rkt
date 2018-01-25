#lang sweet-exp racket

define imp-sum(lst)
  define s 0
  for ([x lst])
    set! s {s + x}
  s

define func-sum(lst)
  let loop ([acc 0]
            [l lst])
    cond
      empty?(l)
        acc
      else
        define first car(l)
        define rest  cdr(l)
        loop {acc + first} rest

define L
  for/list ([i in-range(10)]) i

imp-sum L
func-sum L
