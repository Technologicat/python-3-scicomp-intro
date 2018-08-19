#lang sweet-exp racket

;; Pythonic decorators for Racket.

require syntax/parse/define
require racket/splicing

provide decorate define/decorated make-decorator define/decorator

;; Apply multiple decorators almost-pythonically
define-syntax-parser decorate
  [_ deco0 ... function]
    syntax
      let ([decos (reverse (list deco0 ...))])
        for/fold
          ([f function])  ; acc
          ([d decos])     ; seq
          d f

;; Preserve function name - for named functions.
;; argspec uses the same syntax as λ (unlike define itself).
;; (Hence the -0, this is not quite what we want.)
define-syntax-parser define/decorated0
  [_ deco0 ... (head argspec body ...+)]
    syntax
      splicing-let ([head (λ argspec body ...)])  ; LHS must be "head" to keep object-name
        define head  ; new head
          decorate
            deco0
            ...
            head  ; old head

;; Version using the same function definition syntax as define itself.
;; Define first, then overwrite, like Python.
define-syntax-parser define/decorated
  [_ deco0 ... (~and (define-args ...+)
                     ((head _ ...) _ ...+))]
    syntax
      begin
        define define-args ...
        set! head
          decorate
            deco0
            ...
            head

;; Helpers to ease writing decorators.
;;
define prefix-sym(pre sym)
  string->symbol
    format "~a~a" pre sym

;; name should be symbol or string; it's the prefix for the object-name of the decorated procedure.
define-syntax-parser make-decorator0
  [this-stx name call f kw kv args body ...]
      syntax
        let ([pre (format "~a-" name)])
          λ　(f)
            procedure-rename
              make-keyword-procedure
                λ (kw kv . args)
                  define-syntax call(_) #'(keyword-apply f kw kv args)
                  body
                  ...
              prefix-sym pre (object-name f)

;; Here f, kw, kv, args break hygiene to let the client code refer to and set! them.
;; Use (call) to call the original f with the current kw, kv, args.
define-syntax-parser make-decorator
  [this-stx name body ...]
    with-syntax ([call (datum->syntax #'this-stx 'call)]
                 [f (datum->syntax #'this-stx 'f)]
                 [kw (datum->syntax #'this-stx 'kw)]
                 [kv (datum->syntax #'this-stx 'kv)]
                 [args (datum->syntax #'this-stx 'args)])
      syntax
        make-decorator0 name call f kw kv args body ...

;; Abbreviation for decorators that don't need arguments.
;; (Ones that do need more complex definitions anyway.)
define-syntax-parser define/decorator
  [this-stx name body ...]
    with-syntax ([call (datum->syntax #'this-stx 'call)]
                 [f (datum->syntax #'this-stx 'f)]
                 [kw (datum->syntax #'this-stx 'kw)]
                 [kv (datum->syntax #'this-stx 'kv)]
                 [args (datum->syntax #'this-stx 'args)])
      syntax
        define name
          make-decorator0 (syntax->datum #'name) call f kw kv args body ...

module+ main
  ;; Defining decorators
  ;;
  define hello(f)
    procedure-rename  ; have a nice object-name, a bit like Python's @wraps.
      make-keyword-procedure  ; def decorated ...
        λ (kw kv . args)
          displayln "hello!"
          keyword-apply f kw kv args
      prefix-sym "hello-" (object-name f)
  ;
  ;; decorator that takes arguments, works similarly as in Python.
  define hello-parametric(s)    ; decorator factory
    define pre (format "~a-" s)
    λ (f)                       ; decorator
      procedure-rename
        make-keyword-procedure  ; def decorated ...
          λ (kw kv . args)
            displayln s
            keyword-apply f kw kv args
        prefix-sym pre (object-name f)
  ;
  define traced(f)
    procedure-rename
      make-keyword-procedure
        λ (kw kv . args)
          displayln (format "calling ~a" f)
          keyword-apply f kw kv args
          displayln (format "called ~a" f)
      prefix-sym "traced-" (object-name f)
  ;
  ;; Using decorators
  ;;
  ;; raw Racket; each level needs more indentation
  define f
    hello
      traced
        λ (x)
          displayln x
  f 42
  ;
  ;; test the object-name handling
  define f2(x)
    {2 * x}
  define f3 traced(traced(f2))
  displayln (object-name f3)
  f3 42
  ;
  define g
    decorate
      hello   ; outer
      traced  ; inner, applied first
      λ (x)
        displayln x
  g 42
  ;
  define/decorated0
    hello
    traced
    h (x)  ; same syntax as in λ.
      displayln x
  h 42
  ;
  ;; The best option:
  define/decorated
    hello-parametric("hello world!")
    traced
    h2(x)  ; same syntax as in define.
      displayln x
  h2 42
  ;
  ;; Using the helpers to define decorators
  ;;
  define hello3
    make-decorator 'hello3
      displayln (format "hello3: before ~a" f)  ; magic "f" is the original function
      call()
      displayln (format "hello3: after ~a" f)
  ;
  define hello4
    make-decorator0 'hello4 call f kw kv args   ; this is the actual implementation...
      displayln (format "hello4: before ~a" f)
      call()
      displayln (format "hello4: after ~a" f)
  ;
  define/decorator hello5                       ; abbreviated form
    displayln (format "hello5: before ~a" f)
    call()
    displayln (format "hello5: after ~a" f)
  ;
  define hello-parametric2(s)
    make-decorator (format "hello-parametric2(\"~a\")" s) 
      displayln s
      call()
  ;
  define/decorated
    hello3
    h3(x)
      displayln x
  h3 42
  ;
  define/decorated
    hello4
    h4(x)
      displayln x
  h4 42
  ;
  define/decorated
    hello5
    h5(x)
      displayln x
  h5 42
  ;
  define/decorated
    hello-parametric2("hi neighborhood!")
    h6(x)
      displayln x
  displayln (object-name h6)
  h6 42
  ;
  ;; What else can we do?
  define/decorator inject-42
    set! args (cons 42 args)  ; magic "args" are the current positional args.
    define result call()
    {2 * result}
  define/decorated
    inject-42
    foo(x)
      x
  foo()  ; look ma no arguments
