#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Make new words statistically similar to a target word list.

The algorithm is based on Markov chains.

Requires a word list; get one e.g. here:

  https://github.com/dwyl/english-words

(The example uses words_alpha.txt.)

Created on Mon Jul  2 16:57:11 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

from collections import Counter

import random
import time

def ngrams(word, n):
#    # http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
#    return ("".join(letters) for letters in zip(*[word[i:] for i in range(n)]))
    return (word[i:(i+n)] for i in range(len(word) - n + 1))  # not pythonic, but a bit faster


# Database for state transitions.
#
# Let's do this functionally without OOP, even though practically all of these
# functions mutate the database. (Too expensive to copy, so we want mutation.)
#
# database: dict,
#    str (length: == overlap) -> str (length: == seglength - overlap)

def database_init():
    return {}

# Markov chain build helper.
#
# Given ngrams from a word, and an integer 0 < k < n, find in this word, which
# (n - k) letters may follow, if we are given the first k letters of an ngram.
#
def database_add_chains(database, ngrams, k):
    for ngram in ngrams:
        pre, suf = ngram[:k], ngram[k:]
        if pre not in database:
            database[pre] = Counter()
        database[pre][suf] += 1

# Padding lengths:
#   The state of the word generator is initialized to overlap*fillvalue.
#   Each state transition produces (seglength - overlap) more letters.
#
def database_add_chains_from_word(database, word, seglength, overlap, fillvalue):
    padded_word = "{}{}{}".format(overlap*fillvalue,
                                  word,
                                  (seglength - overlap)*fillvalue)
    database_add_chains(database, ngrams(padded_word, seglength), overlap)

# Convert the counters to cumulative distribution functions
def database_finalize(database):
    for pre in database:
        counters = database[pre]
        sufs = sorted(counters.keys())
        n = sum(counters.values())

        out = []
        s = 0.  # cumulative probability
        for suf in sufs[:-1]:
            p = counters[suf] / n
            s += p
            out.append((p, s, suf))

        if len(sufs):
            suf = sufs[-1]
            p = counters[suf] / n
            out.append((p, 1., suf))  # avoid rounding errors in s in last item

        database[pre] = tuple(out)  # replace raw Counter with CDF data

# mutates existing_words! (to prevent duplicates in output)
def make_new_word(database, existing_words, overlap, fillvalue, *,
                  max_tries=1000, advance=None, require_new=True):
    def random_advance(database, state):
        x = random.uniform(0., 1.)
        for p,s,more in database[state]:  # convert distribution via CDF
            if x < s:
                break
        return p, s, more
    advance = advance or random_advance

    # Try until we get a word not already in the wordlist.
    # Sensible only because the space of possible words is huge.
    tries = 0
    while True:
        tries += 1

        # Essentially an unfold.
        word = ""
        trace = []
        state = overlap*fillvalue
        while True:
            p, s, more = advance(database, state)

            word += more.rstrip(fillvalue)

            oldstate = state
            state = (state + more)[-overlap:]  # NOTE: len(state + more) == seglength

            trace.append((oldstate, state, p, "{}->{} ({:g}%)".format(oldstate, state, 100.*p)))

            if more[-1] == fillvalue:  # end word?
                break

        if not require_new or word not in existing_words or tries >= max_tries:
            break

    existing_words.add(word)  # prevent duplicates in output

    if tries >= max_tries:
        print("WARNING: max_tries = {} exceeded, word '{}' is not new.".format(max_tries, word))

    return (word, tries, trace)

# Follow maximum p at each step and see what we get.
def maxp_word(database, existing_words, overlap, fillvalue, max_tries=1000):
    def maxp_advance(database, state):
        return max(database[state], key=lambda item: item[0])  # p, s, more
    return make_new_word(database, existing_words, overlap, fillvalue,
                         max_tries=max_tries, advance=maxp_advance, require_new=False)

# Follow minimum p at each step and see what we get.
def minp_word(database, existing_words, overlap, fillvalue, max_tries=1000):
    def minp_advance(database, state):
        return min(database[state], key=lambda item: item[0])  # p, s, more
    return make_new_word(database, existing_words, overlap, fillvalue,
                         max_tries=max_tries, advance=minp_advance, require_new=False)

def main():
    nout = 100     # how many words to make
    seglength = 6  # (letters) segment length for analysis
    overlap = 5    # (letters) between adjacent segments in Markov chain

    inputfile = "words_alpha.txt"  # https://github.com/dwyl/english-words

    # Works for Finnish, too.
    # http://kaino.kotus.fi/sanat/nykysuomi/
    # http://linja-aho.blogspot.com/2010/08/suomen-kielen-sanalista.html
#    inputfile = "kotus_sanat.txt"
#    inputfile = "kielitoimisto2018.txt"

    assert seglength > 0
    assert 0 < overlap < seglength

    print("Segment length {}, overlap {}, input {}.".format(seglength, overlap, inputfile))

    fillvalue = "*"  # any single character that is not a valid letter

#    wordlist = ("catamaran", "adventurous")
    with open(inputfile, mode="rt", encoding="utf-8") as file:
        wordlist = [line.strip().lower() for line in file]
    existing_words = set(wordlist)

    # Build the database for the Markov chains
    database = database_init()

    t0_total = time.time()
    t0 = t0_total
    for j,word in enumerate(wordlist):
        # must be really fast per iteration; don't call time.time() too often.
        if j % 10000 == 0 and time.time() - t0 > 1.:
            print("analyzing {}/{}: '{}'".format(j+1, len(wordlist), word))
            t0 = time.time()
        database_add_chains_from_word(database, word, seglength, overlap, fillvalue)
    dt_total = time.time() - t0_total
    print("  input analyzed in {:g}s ({:g} words; {:g} words/s)".format(dt_total, len(wordlist), len(wordlist) / dt_total))

    t0_total = time.time()
    database_finalize(database)
    dt_total = time.time() - t0_total
    print("  distributions computed in {:g}s ({:g} entries; {:g} entries/s)".format(dt_total, len(database), len(database) / dt_total))

    print("max-p and min-p words (from this input, with current parameters):")
    from functools import reduce as foldl
    from operator import mul
    product = lambda iterable: foldl(mul, iterable)
    word_p = lambda trace: product(p for _,_,p,_ in trace)
    for f in (maxp_word, minp_word):
        word,tries,trace = f(database, existing_words, overlap, fillvalue)
        print("  {} (p = {:g})".format(word, word_p(trace)))

    # Make new words
    out = sorted([make_new_word(database, existing_words, overlap, fillvalue)
                 for _ in range(nout)])
    print(tuple(word for word,tries,trace in out))

#    # State traces with probabilities, debug output
#    indent = 4 * " "
#    for word,tries,trace in out:
#        print("{} (p = {:g})".format(word, word_p(trace)))
#        for oldstate,state,p,desc in trace:
#            print(indent + desc)

    tries_data = [tries for word,tries,trace in out]
    mean_tries = sum(tries_data) / len(tries_data)
    print("Tries made mean {}, max {}.".format(mean_tries, max(tries_data)))

if __name__ == '__main__':
    main()
