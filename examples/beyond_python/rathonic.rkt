#!/usr/bin/env racket
#lang sweet-exp racket

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; rathonic: Python-inspired syntax elements for Racket
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Mainly an exercise in syntax-parse.
;;
;; You're quite mad if you use this for anything serious!
;;
;; But feel free to lift any useful bits.


;; The return and while statements likely don't play well with Racket's exception mechanism.
;;
;; For a complete solution with return, while and a custom exception mechanism,
;; see this post by Matthew Might:
;;   http://matt.might.net/articles/implementing-exceptions/
;;
;; (Rathonic implements just the return and while parts of that.)


;; TODO: unpack-dict macro to convert a hash to keyword arguments
;; TODO: for-else (requires some thought as to which features we want to support and with what syntax)

provide( nfx  ; for sweet-exp's {} infix math hook; supports ** * / + - or and
         ;
         **  ; (exponentiation only)
         ;
         def
         ;
         zip zip< zip> map< map>  ; equal-length-only, shortest, longest-with-fill
         ;
         import from
         ;
         ; functions and lambdas that use return must be defined using
         ; one of the /return forms.
         return define/return def/return lambda/return λ/return
         ;
         while continue break
         ;
         list->values values->list values-ref  ; rackety multiple-values utils
         ;
         unpack define/unpack <-               ; pythonic list --> multiple-values
         let/unpack let*/unpack letrec/unpack  ; like define/unpack, in let form
         ;
         unpacking-sequence  ; list-of-lists --> sequence of multiple-values
                             ; (convenient for iteration of lols using Racket's
                             ;  for forms with the multiple-values syntax)
         for/unpack
         ;
         lc  ; list comprehension
         sc  ; set comprehension
         dc  ; dict comprehension
         ;
         u:name    ; unicodedata.name
         u:lookup  ; unicodedata.lookup
       )


require for-syntax(syntax/parse
                   only-in(racket/syntax format-id)
                   only-in(racket/sequence in-syntax))

require only-in("infix5.rkt" nfx)
require only-in("zip2.rkt" zip zip< zip> map< map>)
require only-in("values-listify.rkt" list->values values->list values-ref)
require only-in("unicodedata.rkt" [name u:name] [lookup u:lookup])
require only-in("abbrev.rkt" abbrev)
require only-in("return.rkt" return define/return lambda/return λ/return)
require only-in("while-else.rkt" while break continue)

abbrev define def
abbrev define/return def/return
abbrev expt **
abbrev list->values unpack

module+ main
  ;; sweet-exp's infix math
  {#f and #f or #t}
  {2 * 3 + 4}
  let* ([x 1]
        [y {9 * 10 ** 3 + x}])
    if {y > 9000}
      'over-9000
      #f
  ;; this also works, because:
  ;;  - sweet-exp itself implements nfx for the special case where all ops are the same
  ;;  - Racket's < is variadic
  {1 < 2 < 3}
  ;; unicodedata
  for ([c '(λ ∂ あ)])
    displayln format("~a is ~a" c u:name(c))
  for ([s '("BLACK STAR" "WHITE STAR" "LOZENGE")])
    displayln format("~a is ~a" s u:lookup(s))

;; The import syntax is modelled after this old Python spec, and then racketified slightly:
;;     https://docs.python.org/2.0/ref/import.html
;;
;; import_stmt:    "import" module ["as" name] ("," module ["as" name] )* 
;;               | "from" module "import" identifier ["as" name]
;;                 ("," identifier ["as" name] )*
;;               | "from" module "import" "*" 
;; module:         (identifier ".")* identifier

;; import foo                  --> (require (prefix-in foo: foo))
;; import foo as bar           --> import (foo as bar)
;; import (foo as bar)         --> (require (prefix-in bar: foo))
;; import foo (bar as baz) qux --> (begin (require ...) ... (require ...))
;;
define-syntax (import stx)
  syntax-parse stx
    #:datum-literals (as)
    [(_) (raise-syntax-error 'import "missing module name" stx)]
    [(_ modname as asname) #'(import (modname as asname))]  ; desugar
    [(_ (modname as asname))
     with-syntax( ([prefix format-id(stx #:source stx "~a:" syntax-e(#'asname))])
         #'require(prefix-in(prefix modname)))]
    ;; must come after (modname as asname), otherwise the whole list will match as "modname"
    [(_ modname) #'(import (modname as modname))]
    [(_ spec0 spec1 ...) #'(begin (import spec0) (import spec1) ...)]

;; from foo import bar                             --> (require (only-in bar foo))
;; from foo import bar as baz                      --> (require (rename-in foo [bar baz]))
;; from foo import (bar as baz) barf (qux as quux) --> (begin ...)
;;
;; We don't support "from foo import *", to allow "from racket import * as mul".
;; If you need that, just use plain (require foo) instead.
;;
;; TODO: improve syntax errors (esp. missing asname)
define-syntax (from stx)
  syntax-parse stx
    #:datum-literals (from import as)
    [(_) (raise-syntax-error 'from "missing module name" stx)]
    [(_ modname) (raise-syntax-error 'from "missing literal 'import'" stx)]
    [(_ modname import) (raise-syntax-error 'from "missing name(s) to import" stx)]
    ; from module import name as asname
    [(_ modname import name as asname) #'(from modname import (name as asname))]
    ; from module import (name0 as asname0) (name1 as asname1) ...
    [(_ modname import (name as asname)) #'require(only-in(modname [name asname]))]
    ; from module import name0 ...
    [(_ modname import name) #'require(only-in(modname name))]
    ; inductive case
    [(_ modname import spec0 spec1 ...) #'(begin (from modname import spec0)
                                                 (from modname import spec1) ...)]

;; test imports
module+ main
    import "zip2.rkt" as zip2
    from "zip2.rkt" import (map> as map-longest) (map< as map-shortest) zip
    define a '(1 2 3)
    define b '(4 5 6)
    zip2:zip(a b)
    map-longest(list a b)
    map-shortest(list a b)
    from racket import * as mul  ; rathonic is not Python, * is just a name
    (mul 2 4)

;module+ main
;    import ("compose.rkt" as compose-mod) "rem-dups-artyom.rkt"
;    compose-mod:compose
;    rem-dups-artyom.rkt:rem-dups
;    from "compose.rkt" import compose
;    compose


;; "tuple unpacking", i.e. destructuring bind

;; unpack a list (this is list->values from values-listify.rkt)
;;
;; '(1 2 3) --> values 1 2 3
;;
;define unpack(lst)
;  apply values lst

;; Python's a,b,c = *L
;;
;; define/unpack a b c <- lst  -->  define-values([a b c] unpack(lst))
;;
;; TODO: at runtime, check that there are length(lst) vars, complain if not
;;
define-syntax (<- stx) (raise-syntax-error '<- "not meaningful outside /unpack forms" stx)
define-syntax (define/unpack stx)
  syntax-parse stx
    #:literals (<-)
    [(_ var0 ... <- lst) #'define-values((var0 ...) unpack(lst))]


;; unpacking-sequence: unpack a list of lists
;;
;; - one iterator object (like required by Racket's "for")
;; - multiple values per iteration
;;
;; '((1 2 3) (4 5 6)) --> values 1 2 3, values 4 5 6
;;
;; how to define custom sequence types in Racket:
;; https://docs.racket-lang.org/reference/sequences.html
;;
struct unpacking-iterator (lol)
  #:methods gen:stream
  [(define (stream-empty? iter)
     (define lol (unpacking-iterator-lol iter))
     (null? lol))
   (define (stream-first iter)
     (define lol (unpacking-iterator-lol iter))
     (unpack (car lol)))
   (define (stream-rest iter)
     (define lol (unpacking-iterator-lol iter))
     (unpacking-iterator (cdr lol)))]

define (make-unpacking-iterator us)
  (unpacking-iterator (unpacking-sequence-lol us))

struct unpacking-sequence (lol)
  #:property prop:sequence
  make-unpacking-iterator


;; Unpacking let forms. These expand to let-values.
;;
;; Any bindings using <- will be expanded, while any bindings
;; of a single identifier are sugared to make the unpacking let
;; have essentially the same syntax as the corresponding regular let
;; (without -values).
;;
;;   let/unpack ([a b c <- lst] [d 42]) body ...
;;   -->
;;   let-values ([(a b c) (unpack lst)] [(d) 42]) body ...
;;
;; let*/unpack, letrec/unpack are defined similarly.
;;
;; TODO: implementation could be parametrized by a macro-generating macro since we
;;       generate the same expansion for each form, but perhaps this is more readable.
;;
define-syntax let/unpack(stx)
  syntax-parse stx
    [(_ bindings body ...)
       (with-syntax ([b unpack-in-bindings(#'bindings)])
         #'(let-values b body ...))]

define-syntax let*/unpack(stx)
  syntax-parse stx
    [(_ bindings body ...)
       (with-syntax ([b unpack-in-bindings(#'bindings)])
         #'(let*-values b body ...))]

define-syntax letrec/unpack(stx)
  syntax-parse stx
    [(_ bindings body ...)
       (with-syntax ([b unpack-in-bindings(#'bindings)])
         #'(letrec-values b body ...))]

define-syntax for/unpack(stx)
  syntax-parse stx
    [(_ bindings body ...)
       ; In the case of for, don't sugar, because:
       ;  - for accepts single-identifier bindings without the parens, so no need to.
       ;  - keywords + values are given in separate items in the bindings list.
       ;    E.g. in "#:when (even? i)", "#:when" is processed first, and then the
       ;    processor sees only "(even? i)", which looks like "var0 item0",
       ;    leading to an error.
       (with-syntax ([b unpack-in-bindings(#'bindings 'unpacking-sequence #f)])
         #'(for b body ...))]

begin-for-syntax  ; helper function for the unpacking "let" and "for" forms
  ; Just a regular function that runs in the transformer environment (phase 1).
  ; TODO: why doesn't a kwarg work here? (complains about unbound id at call site)
  define error-msg #f
  define unpack-in-bindings(stx [proc-sym 'unpack] [sugar #t])
    with-syntax ([proc datum->syntax(stx proc-sym)])  ; proc-sym -> syntax, look up binding at runtime
      for/list ([item in-syntax(stx)])
        syntax-parse item #:datum-literals (<-)
          [[var0 ... <- lst] #'[(var0 ...) proc(lst)]]  ; process the unpack syntax
          ; if sugar enabled, sugar one-id case to look like regular let
          [[var0 item0] #:fail-unless sugar error-msg #'[(var0) item0]]
          [anything-else #'anything-else]  ; pass through everything else


module+ main
  define lst '(a b c)
  unpack lst  ; --> values 'a 'b 'c
  ;
  define/unpack x2 y2 z2 <- lst
  displayln(format("~a, ~a, ~a" x2 y2 z2))
  ; desugars into
  define-values (x1 y1 z1) (unpack lst)
  displayln(format("~a, ~a, ~a" x1 y1 z1))
  ;
  let/unpack ([a b c <- lst] [d 10])
    displayln(format("~a, ~a, ~a, ~a" a b c d))
  ; desugars into
  let-values ([(a b c) (unpack lst)] [(d) 10])
    displayln(format("~a, ~a, ~a, ~a" a b c d))
  ;
  ; - "apply" unpacks in a function call, as usual in Racket
  ; - "unpack" generates multiple-values, not an argument list
  ; - so use "apply" here!
  ;define zipped zip('(1 2 3) '(4 5 6) '(7 8 9))
  define zipped (apply zip '((1 2 3) (4 5 6) (7 8 9)))
  ;
  for/unpack ([x y z <- zipped]) (displayln (list x y z))
  ; desugars into
  for ([(x y z) (unpacking-sequence zipped)]) (displayln (list x y z))
  ; where unpacking-sequence converts a list-of-lists into a sequence of multiple-values.
  ;
  ; for/unpack passes through everything else:
  for/unpack ([x y z <- zipped]
              [i in-naturals(0)]
              #:when odd?(i)) (displayln (list x y z))


;; pythonic list and set comprehensions
;;
;; (lc expr for var0 ... in lst0 ...)    ; bind multiple sequences explicitly, like Racket
;; (lc expr for var0 ... in values seq)  ; sequence returning multiple-values, like Racket
;; (lc expr for var0 ... in unpack lol)  ; unpack one level of list wrapping, like Python
;; (lc expr for var0 ... in lst0 ... if pred)
;; (lc expr for var0 ... in values seq if pred)
;; (lc expr for var0 ... in unpack lol if pred)
;;
require (for-meta 2 (only-in syntax/parse syntax-parse))
require (for-meta 2 racket/base)
begin-for-syntax
  ;; phase-2 macro to create a phase-1 syntax transformer for a pythonic(-ish) comprehension form.
  ;;   self: identifier that this transformer will be bound to, used in recursive rules and in
  ;;         error messages. The returned transformer must be define-syntax'd to this name separately.
  ;;   looper: identifier such as for/list, for/set, for/hash
  ;;   pat: pattern to match in the value part (before literal "for") of the comprehension form
  ;;
  ;;   body: expression for iteration body, can use pattern variables bound by pat
  define-syntax make-comprehension-transformer(args-stx)
    ; Because we nest syntax-parse, we must escape any ... that is intended
    ; for the inner syntax-parse; otherwise the outer one will capture it.
    ;
    ; There are two ways to do this:
    ;   - use (... ...); a block that begins with "(..." treats ... literally
    ;       https://lists.racket-lang.org/users/archive/2010-July/040767.html
    ;       https://stackoverflow.com/a/38276125
    ;   - using quote-syntax, create a constant representing a literal ellipsis
    ;       https://stackoverflow.com/a/38276476
    syntax-parse args-stx
      [(_ self looper pat ... body)
      #:with ooo (quote-syntax ...)
      #'(let ([my-name syntax->datum(#'self)])
         (λ (stx)
          (syntax-parse stx
              #:datum-literals (for in if unpack values)
              [(_ pat ... for var0 ooo in lst0 ooo if)
                 (raise-syntax-error my-name "if: missing predicate" stx)]
              [(_ pat ... for var0 ooo in)
                 (raise-syntax-error my-name "missing input specification" stx)]
              ; with if and unpack parts
              [(_ pat ... for var0 ooo in unpack lol if pred)  ; this "unpack" is literal
                 #'(self pat ... for var0 ooo in values unpacking-sequence(lol) if pred)]
              [(_ pat ... for var0 ooo in values seq if pred)  ; this "values" is literal
                 #'looper( ([(var0 ooo) seq] #:when pred) body )]
              ; with if part
              [(_ pat ... for var0 ooo in lst0 ooo if pred)
                 cond([not{length(syntax->datum(#'(var0 ooo))) = length(syntax->datum(#'(lst0 ooo)))}
                        (raise-syntax-error my-name "must have as many input sequences as vars" stx)])
                 #'looper( ([var0 lst0] ooo #:when pred) body )]
              ;; base: generate if part if not present. Works for all variants.
              ;; At this level, "unpack lol" and "values seq" appear the same as "lst0 lst1".
              [(_ pat ... for var0 ooo in terms ooo)
                 #'(self pat ... for var0 ooo in terms ooo if #t)]
              [(_) (raise-syntax-error my-name "missing value part" stx)]
              [(_ pat ...) (raise-syntax-error my-name "missing literal 'for'" stx)]
              [(_ pat ... for) (raise-syntax-error my-name "missing var0 ..." stx)]
              [(_ pat ... anything) (raise-syntax-error my-name "expected literal 'for'" stx)]
              ;; the literal "in" signals the end of varlist, so we can't tell if missing or typoed.
              [(_ pat ... for var0 ooo) (raise-syntax-error my-name "no literal 'in'" stx)]
              ;; for non-trivial pat (dictcomp)
              [(_ anything ooo) (raise-syntax-error my-name "bad syntax in value part" stx)])))]
  define transform-listcomp make-comprehension-transformer(lc for/list expr expr)
  define transform-setcomp  make-comprehension-transformer(sc for/set  expr expr)
  define transform-dictcomp make-comprehension-transformer(dc for/hash k : v (values k v))

define-syntax (lc stx) transform-listcomp(stx)
define-syntax (sc stx) transform-setcomp(stx)
define-syntax (dc stx) transform-dictcomp(stx)

module+ main
  lc (* x x) for x in '(1 2 3)
  ;lc (* x y) for x y in '(1 2 3)  ; error case, missing a list
  lc (* x y) for x y in '(1 2 3) '(4 5 6)              ; rathonic approach: list wrapper not needed
  lc (* x y) for x y in unpack zip('(1 2 3) '(4 5 6))  ; pythonic approach
  ;; no enumerate(), since Racket already has in-naturals and in-indexed which do the same thing:
  lc format("~a: ~a" i x) for x i in values in-indexed('(a b c))
  lc format("~a: ~a" i x) for i x in in-naturals(0) '(a b c)
  lc format("~a: ~a" i x) for i x in unpack zip<(in-naturals(0) '(a b c))
  ;; predicates
  lc (* x y) for x y in '(1 2 3) '(4 5 6) if (odd? x)
  lc (* x y) for x y in '(1 2 3) '(4 5 6) if (odd? (* x y))
  ;; set comprehension (same features as lc)
  sc x for x in '(a b c)
  sc (* x y) for x y in '(1 2 3) '(4 5 6)
  ;; dict comprehension (same features as lc)
  dc x : (* x x) for x in '(1 2 3)
  dc x : (* x y) for x y in '(1 2 3) '(4 5 6)
  dc x : (* x y) for x y in unpack zip('(1 2 3) '(4 5 6))
  dc i : x for x i in values in-indexed('(a b c))
  dc i : x for i x in in-naturals(0) '(a b c)
  dc i : x for i x in unpack zip<(in-naturals(0) '(a b c))
