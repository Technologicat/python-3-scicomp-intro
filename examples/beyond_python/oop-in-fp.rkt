#lang sweet-exp racket

;; A simple class, built on (lexical) closures.
;;
;; Useful patterns:
;;   - let over lambda: local (instance) variables
;;   - lambda over let over lambda: object constructor
;;   - (let over lambda) over (let over lambda): static variables,
;;     shared among instances of the same class
;;
;; See:
;;   Doug Hoyte: Let Over Lambda -- 50 Years of Lisp
;;   https://letoverlambda.com/textmode.cl/guest/chap2.html#sec_5
;;
;;   A koan about objects and closures:
;;   http://people.csail.mit.edu/gregs/ll1-discuss-archive-html/msg03277.html
;;
;;   OOP in FP, including inheritance:
;;   http://okmij.org/ftp/Scheme/oop-in-fp.txt
;;
;;   Delegation is inheritance:
;;   http://wiki.c2.com/?DelegationIsInheritance

;; This function bootstraps the type T, creating the constructor.
;;
;; The initial values of static variables can be provided as arguments.
;;
define bootstrap-T(s0)
  let ([s s0])  ; static variable, shared between instances of T
    ;; internal definitions - static methods
    define get-s()
      s
    define set!-s(x)
      set! s x
    define make(a0)  ; constructor for instances of T
      let ([a a0])   ; instance variable
        ;; internal definitions - instance methods
        define get-a()
          a
        define set!-a(x)
          set! a x
        ;; dispatcher - returned by the constructor
        ;; (this is the closure representation of an object instance of type T)
        λ (op)
          case op
            (set!-s) set!-s  ; dispatch to static method, by lexical scoping
            (get-s)  get-s
            (set!-a) set!-a
            (get-a)  get-a
    ;; dispatcher - returned by bootstrap-T()
    ;; (this is the closure representation of the class T)
    λ (op)
      case op
        (set!-s) set!-s
        (get-s)  get-s
        (make)   make

;; The constructor should be a singleton, to get all instances
;; of T to see the same instance of the static variables.
;; (Each call to bootstrap-T() creates a new instance of the static variables!)
define T bootstrap-T(42)

;; Rackety accessors, taking the object instance as the first argument.
;;
;; This is similar to how fields of Racket structs are accessed.
;;   https://docs.racket-lang.org/guide/define-struct.html
define T-get-s(self)    self('get-s)()
define T-set!-s(self x) self('set!-s)(x)
define T-get-a(self)    self('get-a)()
define T-set!-a(self x) self('set!-a)(x)

module+ main
  ;; Create some instances of T
  define T1 T('make)(1)
  define T2 T('make)(2)
  ;; Get values of the static and instance variables.
  T1('get-s)() ; 42
  T2('get-s)() ; 42
  T1('get-a)() ; 1
  T2('get-a)() ; 2
  ;; Mutate static variable.
  T1('set!-s)(23)
  T1('get-s)() ; 23
  T2('get-s)() ; 23
  ;; Can also access the static variable directly via the class.
  T('set!-s)(0)
  T('get-s)()  ; 0
  T1('get-s)() ; 0
  T2('get-s)() ; 0
  ;; Mutate instance variables.
  T1('set!-a)(3)
  T2('set!-a)(5)
  T1('get-a)() ; 3
  T2('get-a)() ; 5
  ;; Rackety accessors.
  T-set!-a(T1 17)
  T-get-a(T1)
