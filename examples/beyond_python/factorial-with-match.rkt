#lang sweet-exp racket

;; Compute factorial.
;;
;; Pattern matching for overloading by value.

;; recursive process, classic lispy solution
define f-classic-rec(n)
  cond
    {n = 1} 1
    else {n * (f-classic-rec {n - 1})}
(f-classic-rec 4)

;; linear process, classic lispy solution
define f-classic-lin(n)
  let loop ([k n]
            [acc 1])
    cond
      {k = 1} acc
      else (loop {k - 1} {k * acc})
(f-classic-lin 4)

;; recursive process, with match
define f-match-rec(n)
  match n
    1 1
    k {k * (f-match-rec {n - 1})}
(f-match-rec 4)

;; linear process, with match
define f-match-lin(n)
  let loop ([count n]
            [acc 1])
    match count
      1 acc
      k (loop {k - 1} {k * acc})
(f-match-lin 4)

;; with some error handling
define f-bulletproofed(n)
  let loop ([count n]
            [acc 1])
    match count
      (or 0 1) acc
      (? positive? k) (loop {k - 1} {k * acc})
      _ (raise-argument-error 'factorial ">=/c 0" count)
(f-bulletproofed 4)
