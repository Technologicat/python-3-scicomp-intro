#lang sweet-exp racket

;; A rudimentary functional-style quicksort.

define partition(p lst)
  let loop ([l lst]
            [low empty]
            [piv empty]
            [hig empty])
    cond
      empty?(l)
        for/list ([x (list low piv hig)])
          reverse x
      else
        define x (car l)
        cond
          {x < p}
            loop (cdr l) (cons x low) piv hig
          {x = p}
            loop (cdr l) low (cons x piv) hig
          {x > p}
            loop (cdr l) low piv (cons x hig)

define qsort(lst)
  cond
    empty?(lst)
      empty
    else
      ;; In a linked list, using a median-of-3 pivot would cost O(n),
      ;; so we just use the first element as the pivot.
      ;;
      ;; We use nested lists instead of indexing to keep track of
      ;; which elements are to be sorted.
      ;;
      for/list ([l (partition (car lst) lst)])
        cond
          empty?(l)
            empty
          empty?(cdr(l))  ; O(1) check for one-element list
            car l
          else
            qsort l

define flatten(lst)
  let loop ([acc empty]
            [l lst])
    cond
      empty?(l)
        reverse acc
      else
        define x (car l)
        cond
          empty?(x)
            loop acc (cdr l)
          pair?(x)  ; the flatten result is already reversed, so foldl
            loop (foldl cons acc (flatten x)) (cdr l)
          else
            loop (cons x acc) (cdr l)

define quicksort(lst)
  flatten(qsort(lst))

module+ main
  define lst '(2 1 5 3 4 8 9 7 6 0)
  quicksort(lst)
