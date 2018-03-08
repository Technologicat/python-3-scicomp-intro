#lang sweet-exp racket

;; Syntax-parse demo: group arguments to keyword and positional arguments.
;;
;; The explanation of ~and at
;;
;;   https://docs.racket-lang.org/syntax/stxparse-patterns.html#%28tech._head._pattern%29
;;
;; was especially useful. The key ideas are:
;;
;;   - a keyword is not an expr
;;   - ~seq can be used to detect keyword,expr pairs
;;   - ~and can be used to bind a pattern variable to the whole pair
;;
;; See also:
;;
;; https://docs.racket-lang.org/syntax/stxparse-specifying.html#%28form._%28%28lib._syntax%2F
;;    parse..rkt%29._define-syntax-class%29%29
;; https://docs.racket-lang.org/syntax/More_Keyword_Arguments.html
;; https://docs.racket-lang.org/syntax/Optional_Keyword_Arguments.html

require syntax/parse/define

provide group-args

define-syntax-parser group-args
  ;; reducible cases
  ;
  ;; move positional terms from the front to after keywords
  [_
   positional-stuff:expr ...+
   (~and (~seq (~seq k:keyword e:expr) ...+)
         (~seq keyword-stuff ...+))
   maybe-tail ...]
     #'(group-args keyword-stuff ... positional-stuff ... maybe-tail ...)
  ;
  ;; move positional terms between keywords to after keywords
  [_
   (~and (~seq (~seq k1:keyword e1:expr) ...+)
         (~seq keyword-stuff1 ...+))
   positional-stuff:expr ...+
   (~and (~seq (~seq k2:keyword e2:expr) ...+)
         (~seq keyword-stuff2 ...+))
   maybe-tail ...]
     #'(group-args keyword-stuff1 ... keyword-stuff2 ... positional-stuff ... maybe-tail ...)
  ;
  ;; base cases
  ;
  ;; with keywords (now always at the front)
  [_
   (~and (~seq (~seq k:keyword e:expr) ...+)
         (~seq keyword-stuff ...+))
   positional-stuff:expr ...]
     #'(syntax->datum #'((k ...) (e ...) (keyword-stuff ...) (positional-stuff ...)))
  ;
  ;; positional only
  [_ positional-stuff:expr ...]
     #'(syntax->datum #'(positional-stuff ...))


;; testing
module+ main
  group-args #:a 1 #:b 2 3 4 5 #:c 6
  group-args 1 2 3 #:a 1 #:b 2 3 4 5 #:c 6
  group-args 1 2 3 #:a 1 #:b 2 3 4 5
  group-args 1 2 3 4 5
  ;
  ; The first sublist returned by group-args indeed contains keyword objects:
  define lst
    group-args #:a 1 #:b 2 3 4 5 #:c 6
  define-values (kw kv kwd pos) (apply values lst)
  for ([k kw])
    displayln keyword?(k)
