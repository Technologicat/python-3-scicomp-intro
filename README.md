# python-3-scicomp-intro

Informal introduction to Python 3 **for scientific computing**.

## What and for whom

If you MATLAB and/or Fortran, but don't yet Python, and you work or study e.g. in the engineering sciences with no formal background in computer science, IT, or software engineering, this material is for you.

The material is meant to be used on a university course (at any level where the material feels appropriate, depending on your background!), but can also be used for self-study.

We concentrate on Python 3 only, as it is the current version, and legacy support (Python 2) [will end by 2020](http://www.python3statement.org/).

You may also be interested in [Scipy Lecture Notes](https://www.scipy-lectures.org/), a community-maintained online material with a similar (but slightly different) focus.

On the other hand, if you already Python, but don't yet Racket, you may be interested in our two final lectures, which contain a crash course on Racket (beside discussing impure functional programming in Python). In short, [Racket](http://racket-lang.org/) is a modern Lisp, or more specifically, a descendant of Scheme.

### Lecture notes ###

This is **not** a general guide to Python for general-purpose programming. Neither is it completely self-contained. Links to online material are provided, and the reader is expected to follow them where applicable.

The course is split into two parts. The first part is an introduction to Python from a scientific computing viewpoint, hopefully with enough information (and external links) to explain how to get basic things done in Python and in NumPy.

The second part consists of a selection of advanced topics. For example, we cover some of the very basics of software engineering, such as taking advantage of version control (specifically `git`) and linters (automated static code analysis and code style analysis).

### Lecture slides and exercises ###

Also in the slides, the course is split into two parts.

In the first part, the slides go into some more detail on some of the basics and fundamentals of Python, but still, not everything is covered. For example, generators are discussed only in the exercises.

The main scientific libraries are introduced at an overview level, but most of the actual examples are deferred to the exercises. The idea is that the reader already knows how to do the same things in MATLAB, so that section of the slides mainly points out where to find the relevant functions in NumPy, SciPy, SymPy and Matplotlib.

The second part of the course consists of introductory lectures to various advanced topics: parallel computing, the behavior of floating point numbers, software engineering, and functional programming (FP).

The two final lectures, on functional programming, include a very brief crash course on Lisps, specifically [Racket](http://racket-lang.org/). This is for context: to give exposure to concepts from outside the Python community, to better see where Python stands, what it offers and what it does not. Also, it enables one to see (very roughly) how code reduces to [λ-calculus](https://en.wikipedia.org/wiki/Lambda_calculus); and finally, it may give some ideas that can be imported (or even **import**ed) to Python.

See also the README in [the folder containing the slides](lecture_slides/).

Racket code examples are collected into the folder titled [beyond Python](examples/beyond_python/), which also has its own README.

## Status

*Update 03/2019*: Some of the ideas presented in the advanced exercises have been [packaged into a library](https://github.com/Technologicat/unpythonic) and developed further. Some constructs have been renamed for clarity. The library also includes many macros implemented in [MacroPy](https://github.com/azazel75/macropy), allowing changes to the semantics of the language. Taken to its extreme, this approach leads to [dialects](https://github.com/Technologicat/pydialect).

Some code examples have been added after the 2018 implementation finished; see the ``examples/`` folder.

*Final status for the 2018 implementation of the course*:

[Lecture slides](lecture_slides/) are available. The same folder contains also some exercises, with solutions.

Some [Python code examples](examples/) are available.

The [lecture notes](python_scicomp_notes.pdf) are complete, but the slides contain the most up-to-date information. It is intended that the notes and the slides complement each other; they focus on slightly different things.

## Course implementation history

A three-lecture mini-course, in Finnish, based on the lecture notes, was held at the end of the 2017 autumn term, at University of Jyväskylä. This was an optional part of *[Introduction to the mathematics of artificial intelligence](https://helituominen.wordpress.com/kurssit-it/johdatus-tekoalyn-taustalla-olevaan-matematiikkaan-tiep1000-syksy-2017/)*; an implementation of TIEP1000, a varying-topic course in information technology.

In the 2018 spring term, a 11-lecture full course (5 credits) was held at Tampere University of Technology, as *Python 3 for Scientific Computing*; an implementation of RAK-19006, Various Topics in Civil Engineering. For that course, this GitHub repo is the official homepage. (The final lecture was held 25.4.2018; deadline of final assignment submissions was 31.5.2018.)

## License

[CC BY-SA 4.0](LICENSE)

In the lecture notes, [AmdahlsLaw.svg](AmdahlsLaw.svg) is by Wikipedia user Daniels220, and is used under CC BY-SA 3.0.

