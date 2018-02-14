#lang sweet-exp racket

require racket/generator

define fib()
  generator ()
    let loop ([a 0]
              [b 1])
      yield a
      loop(b {a + b})

for/list ([f in-producer(fib())]
          [k in-range(1000)])
  f
