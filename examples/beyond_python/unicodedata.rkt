#lang sweet-exp racket

;; Minimal implementation of pythonic unicodedata,
;; providing name() and lookup().
;;
;; Download the data file from
;;   ftp://ftp.unicode.org/Public/UNIDATA/UnicodeData.txt

provide name lookup

define read-datafile([filename "UnicodeData.txt"])
  define prepend-pair(p lst)
    cons car(p) cons(cdr(p) lst)
  define parse()
    define iter(i->s s->i)
      define line read-line()
      cond
        equal?(eof line)
          cons(i->s s->i)
        else
          define lst string-split(line ";")
          define num-hex list-ref(lst 0)
          define num string->number(num-hex 16)
          define name list-ref(lst 1)
          define num-name cons(num name)
          define name-num cons(name num)
          iter(prepend-pair(num-name i->s)
               prepend-pair(name-num s->i))
    iter empty empty
  with-input-from-file(filename parse #:mode 'text)

define data read-datafile()
define num->name apply(hash car(data))
define name->num apply(hash cdr(data))

;; TODO: catch exceptions and re-raise meaningful errors

;; get name of unicode character
;;
;; for convenience, input can be char, symbol or string (single character)
define name(s)
  define c
    cond
      char?(s)
        s
      {symbol?(s) and {string-length(symbol->string(s)) = 1}}
        string-ref(symbol->string(s) 0)
      {string?(s) and {string-length(s) = 1}}
        string-ref(s 0)
      else
        raise-argument-error('name "character, single-char string or single-char symbol" s)
  define i char->integer(c)
  hash-ref num->name i

;; get unicode character by name
;;
define lookup(s)
  define i hash-ref(name->num s)
  integer->char(i)

;; testing
module+ main
  for ([c '(λ ∂ あ)])
    displayln format("~a is ~a" c name(c))
  for ([s '("BLACK STAR" "WHITE STAR" "LOZENGE")])
    displayln format("~a is ~a" s lookup(s))
