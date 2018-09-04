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

define ntuples(n lst)
   cond
     {n = 1}
       lst
     else
       match lst
        '()
          empty
        [list-rest a rest]
          append
            map
              cond
                {n > 2}
                  curry apply list a
                else
                  curry list a
              ntuples {n - 1} rest
            ntuples n rest

define l '(1 2 3 4 5)
pairs l
triplets l
ntuples 4 l
