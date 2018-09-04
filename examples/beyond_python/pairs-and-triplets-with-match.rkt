#lang sweet-exp racket

define pairs(lst)
   match lst
    '()
      empty
    [list-rest a rest]
      append
        map
          curry list a
          rest
        pairs rest

define triplets(lst)
   match lst
    '()
      empty
    [list-rest a rest]
      append
        map
          curry apply list a
          pairs rest
        triplets rest

pairs '(1 2 3 4)
triplets '(1 2 3 4)
