# Beyond Python

Programming is a dynamic discipline. It is likely that also in the scientific computing community, the approach to programming will continue to evolve in the decades to follow.

How to extrapolate the future?

When viewed in terms of programming paradigms and tools, because computational scientists are not software engineers, in many areas the computational science community tends to trail behind the mainstream programming community. Roughly speaking, object-oriented programming, which has been mainstream in the programming community since the 1980s-90s, has found its way into scientific codes during the last 10-20 years.

(There are notable exceptions where the computational science community is the better informed one, such as parallelization, and the [fine details of floating point numbers](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html), since these are highly relevant to computing correct answers quickly.)

Right now, [functional programming](https://en.wikipedia.org/wiki/Functional_programming) (FP) is trending toward mainstream. Although strictly speaking, the following only amounts to anecdotal evidence, the signs seem clear: there is the popularity of [Haskell](https://en.wikipedia.org/wiki/Haskell_(programming_language)) in academic circles, as well as the recent rise of functionally flavored languages running on top of the Java [VM](https://en.wikipedia.org/wiki/Virtual_machine), such as [Clojure](https://en.wikipedia.org/wiki/Clojure), [Scala](https://en.wikipedia.org/wiki/Scala_%28programming_language%29) and [Kotlin](https://en.wikipedia.org/wiki/Kotlin_%28programming_language%29). Even Java 8 itself contains some FP features (see e.g. these motivating posts [[1]](http://www.deadcoderising.com/why-you-should-embrace-lambdas-in-java-8/) [[2]](https://flyingbytes.github.io/programming/java8/functional/part1/2017/01/23/Java8-Part1.html)).

Important motivations for FP are improved modularity ([Hughes, 1984](http://www.cse.chalmers.se/~rjmh/Papers/whyfp.html)), and robustness. As Abelson and Sussman argument in their classic textbook [Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html), [mutable state](https://en.wikipedia.org/wiki/Immutable_object) - which is extensively used in the classical imperative programming paradigm - makes the behavior of programs substantially harder to analyze, and introduces whole new categories of possible mistakes, which can be eliminated by favoring an FP approach.

From these observations: it is likely that as tools improve, FP will be mainstream also in scientific codes in (at most) 20-30 years from now.

The future is not yet, so the tools are not yet there; right now, Python is the practical option. Nevertheless, the appropriate time to become familiar with the basic ideas of FP is now; to walk among the pioneers, as well as to be prepared to easily learn more later.

## Which possible future?

It is still difficult to say which particular school of thought, and which programming language, will eventually become dominant. [Haskell](https://en.wikipedia.org/wiki/Haskell_(programming_language))? Some member of the [Lisp](https://en.wikipedia.org/wiki/Lisp_(programming_language)) family? Something completely unexpected?

Haskell is a *pure* functional programming language with strong roots in mathematics (category theory), and comes with a highly advanced static type system. Because no real-world program is completely free of side effects, these are hidden inside ***monads***, a central concept in Haskell that does not appear in most other programming languages.

For our purposes of looking beyond Python, we will concentrate on the other main option - *impure* FP, working in the Lisp family of programming languages. Some of these techniques can be imported (or even **import**ed) into Python; see (see [lecture 11](../../lecture_slides/lectures_tut_2018_11.pdf).

### Monads?

For a mathematician, [a monad is a monoid in the category of endofunctors](https://stackoverflow.com/questions/3870088/a-monad-is-just-a-monoid-in-the-category-of-endofunctors-whats-the-proble%E2%85%BF), but maybe that does not help much.

For a programmer, a monad is a design pattern that generalizes *function composition* (see [lecture 10](../../lecture_slides/lectures_tut_2018_10.pdf), slide 12), helping to simplify code and eliminate lots of boilerplate.

See e.g. these useful practical explanations:
 - [You Could Have Invented Monads! (And Maybe You Already Have.)](http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html),
 - [Monads, part 1: a design pattern](https://www.stephanboyer.com/post/9/monads-part-1-a-design-pattern) (in Python, no less!), and
 - ["What is a monad?" on StackOverflow](https://stackoverflow.com/questions/44965/what-is-a-monad).

If you would like to use monads **in Racket**, see the library [Monads in Racket](https://github.com/tonyg/racket-monad), and the explanatory blog post from the author, [Monads in Dynamically-Typed Languages](http://eighty-twenty.org/2015/01/25/monads-in-dynamically-typed-languages).

If you would like to use monads **in Python**, see e.g.:
 - [PyMonad](https://bitbucket.org/jason_delaat/pymonad/),
 - [OSlash](https://github.com/dbrattli/OSlash),
 - [Monad-Python](https://github.com/dpiponi/Monad-Python) (with a nice application to computing probability distributions; see [test3.py](https://github.com/dpiponi/Monad-Python/blob/master/test3.py)) and
 - [Monads in Python](http://www.valuedlessons.com/2008/01/monads-in-python-with-nice-syntax.html).

## Lisp

In short, Lisp is a family of *programmable programming languages* ([as pointed out](http://www.paulgraham.com/quotes.html) by John Foderaro) that began in 1958, one year later than Fortran 1. The original language was called LISP (LISt Processor). It is the second oldest high-level language whose direct descendants are still in active use.

Keep in mind that [high-level](https://en.wikipedia.org/wiki/High-level_programming_language) means *anything above assembly*; Lisp, just like Python, operates at a much higher level of abstraction than e.g. Fortran or C.

While Python can be thought of as *executable pseudocode*, Lisp has been called *executable mathematics* ([L. Peter Deutsch](http://www.paulgraham.com/quotes.html)). (Admittedly, at the time of this writing, Haskell also has a valid claim to that title, although for different reasons.)

The distinguishing feature of Lisps is that *the syntax is user-modifiable*, via a feature called [syntactic macros](https://en.wikipedia.org/wiki/Macro_(computer_science)#Syntactic_macros). This is much more powerful than, and should not be confused with, C preprocessor macros. Whereas the C preprocessor performs string substitution, syntactic macros manipulate the [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) by running arbitrary code. The [metalanguage](https://en.wikipedia.org/wiki/Metaprogramming) for writing macros is (all of!) Lisp itself; contrast [generics in C++](https://en.wikipedia.org/wiki/Template_(C++)), where a separate templating mini-language is used.

[Hygienic macros](https://en.wikipedia.org/wiki/Hygienic_macro) are a notable improvement over the early days of LISP, avoiding the issues of *identifier capture* and *free symbol capture* (see [[1]](http://www.phyast.pitt.edu/~micheles/scheme/scheme28.html#the-hygiene-problem) [[2]](https://en.wikibooks.org/wiki/Scheme_Programming/Macros)). [Racket](http://racket-lang.org/) adds a tower of [phase levels](https://docs.racket-lang.org/guide/phases.html); see [this short explanation](http://www.phyast.pitt.edu/~micheles/scheme/scheme22.html) and the paper by [Flatt (2002)](https://www.cs.utah.edu/plt/publications/macromod.pdf). For an introduction to Racket's (highly advanced) macro system, see [Fear of Macros](http://www.greghendershott.com/fear-of-macros/) and [The Racket Guide](https://docs.racket-lang.org/guide/macros.html).

Macros can be used to create abstractions for design patterns that cannot be extracted as functions. Furthermore, macros allow **the user** to add language features that, in most languages, require the language designer's approval, a standardization process, and the distribution of a new language version. For example, Python added a [dedicated matrix multiplication operator](https://www.python.org/dev/peps/pep-0465/) in Python 3.5; whereas in Lisps, a matrix *library* can add that, requiring no changes to the core language.

In fact, the core of many Lisps does not even include a `for` loop - it is not necessary, because iteration is equivalent to [tail recursion](https://stackoverflow.com/questions/33923/what-is-tail-recursion), and macros can be used to add a `for` syntax element if desired. Of course, [the standard library covers this](https://docs.racket-lang.org/reference/for.html); the point is that `for` is implemented in the library, not in the language itself.

Macros facilitate a programming approach somewhat unique to the Lisp community - [bottom-up programming](http://www.paulgraham.com/progbot.html), i.e. bringing the language iteratively closer to the problem domain, until the concepts are at a level that is convenient to use to express the solution. See also [extensible programming](https://en.wikipedia.org/wiki/Extensible_programming), [language-oriented programming](https://en.wikipedia.org/wiki/Language-oriented_programming), and [Felleisen et al. (2018)](https://dx.doi.org/10.1145/3127323).

**A word of caution** when reading about Lisp online: contrary to popular belief, it can be shown ([Felleisen, 1991](http://www.cs.rice.edu/CS/PLT/Publications/Scheme/scp91-felleisen.ps.gz)) that Lisp is **not** an asymptotic limit of programming languages that everything in the Fortran branch is converging toward. As an important example, [first-class](https://en.wikipedia.org/wiki/First-class_citizen) [lazy functions](https://en.wikipedia.org/wiki/Lazy_evaluation) cannot be implemented in a language that only offers [eager (strict) evaluation](https://en.wikipedia.org/wiki/Eager_evaluation), such as most Lisps. In an eager language it is possible to implement lazy evaluation via a *macro* (e.g. Racket [does so](https://docs.racket-lang.org/reference/Delayed_Evaluation.html)), but implementation of this feature via a regular function is not possible. (There is [lazy/racket](https://docs.racket-lang.org/lazy/), but that is a separate language.)

(See [Evaluation strategy in Wikipedia](https://en.wikipedia.org/wiki/Evaluation_strategy) for more. See also [family tree of programming languages](https://www.levenez.com/lang/).)

Generally speaking, each programming language has its strengths and weaknesses. The strength of Lisp is to be able to modify the language to suit one's needs. Some nontrivial examples include:

- [Implementing return, while, and exception handling](http://matt.might.net/articles/implementing-exceptions/) using [call/cc](https://en.wikipedia.org/wiki/Call-with-current-continuation) (see also [continuations](https://beautifulracket.com/explainer/continuations.html); Racket [docs](https://docs.racket-lang.org/reference/cont.html#%28def._%28%28quote._%7E23%7E25kernel%29._call-with-current-continuation%29%29)) and macros
- [Modifying the reader layer to use indentation instead of parentheses](https://srfi.schemers.org/srfi-110/srfi-110.html) (like in Python) (Racket [has a package for this](https://docs.racket-lang.org/sweet/))
- [User-programmable infix operators](https://lexi-lambda.github.io/blog/2017/08/12/user-programmable-infix-operators-in-racket/)
- [Non-deterministic evaluation](http://www.cs.toronto.edu/~david/courses/csc324_w15/extra/choice.html), enumerating through answers that satisfy a given criterion
- [Monads](https://github.com/tonyg/racket-monad)


## Some small examples in Racket

For the purposes of this brief exposition of features beyond what Python offers, we have chosen the Lisp family, and specifically [Racket](http://racket-lang.org/).


## In conclusion

How trying to write Lisp code in Python looks like: [Python Obfuscation #1](http://baruchel.github.io/python/2017/11/16/Python-Obfuscation-01/) (Thomas Baruchel).

In the same spirit,
```Python
f = lambda lst: (lambda seen: [seen.add(x) or x for x in lst if x not in seen])(set())
L = [1, 1, 3, 1, 3, 2, 3, 2, 2, 2, 4, 4, 1, 2, 3]
print(f(L))
```
because Python has no `let`. If it did, we could de-obfuscate this to:
```Python
f = lambda lst:
      let [seen = set()]:
        [seen.add(x) or x for x in lst if x not in seen]
L = [1, 1, 3, 1, 3, 2, 3, 2, 2, 2, 4, 4, 1, 2, 3]
print(f(L))
```

Finally, for an elaborate piece of programming humor, see [Statementless Python](https://gist.github.com/brool/1679908) (which may start to sound vaguely familiar roughly one third the way through).

