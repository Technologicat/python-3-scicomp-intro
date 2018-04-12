#lang sweet-exp racket

require syntax/parse/define

;; manual loop, with named let
define looped-hello(n)
  define last {n - 1}
  let loop ([i 0])  ; "loop" is just a name
    displayln
      format
        "hello from loop, iteration ~a"
        i
    cond
      {i < last}
        loop {i + 1}
(looped-hello 5)

;; syntax parser to template that
define-syntax-parser for-range
  [_ (counter start end) body ...]
    syntax
      let ([last {end - 1}])
        let loop ([counter start])
          body
          ...
          cond
            {counter < last}
              loop {counter + 1}

;; so we can use the loop like this:
for-range (i 0 5)
  displayln
    format
      "hi from loop, iteration ~a"
      i
