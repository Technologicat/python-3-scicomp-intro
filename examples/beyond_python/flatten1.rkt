#lang sweet-exp racket

provide flatten1 flatmap applymap

;; Flatten a nested list by one level.
define flatten1(lst)
  let loop ([acc empty]
            [l lst])
    cond
      empty?(l)
        acc
      else
        define item (car l)
        define sublist   ; adaptor for append, because it expects lists
          cond
            pair?(item)
              item
            else
              list item
        loop (append acc sublist) (cdr l)

;; map, then flatten the result by one level.
;;
;; When proc returns a list for each item, this is useful to concatenate
;; the mapping results into a single list.
;;
define flatmap(proc . lsts)
  flatten1 (apply map proc lsts)

;; like Python's itertools.starmap
define applymap(proc lst)
  map (curry apply proc) lst
; equivalent:
;  for/list ([item lst])
;    apply proc item

module+ main
  define a '((1 2) 3 (4 (5 6)) 7)
  flatten1 a
  flatten a  ; in standard library
  ;
  define b (build-list 10 values)
  define f (λ (x) (list x (* x x) (* x x x)))  ; multiple results as a list
  map f b
  flatmap f b
  ;
  define c '((1 2 3) (4 5 6) (7 8 9))
  applymap + c
