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
#        sufs = sorted(counters.keys())  # nicer for debugging but a bit slower
        sufs = tuple(counters.keys())
        n = sum(counters.values())

        out = []
        s = 0.  # cumulative probability
        for suf in sufs[:-1]:
            s += counters[suf] / n
            out.append((s, suf))

        if len(sufs):
            out.append((1., sufs[-1]))  # avoid rounding errors in last item

        database[pre] = tuple(out)  # replace raw Counter with CDF data

# mutates existing_words! (to prevent duplicates in output)
def make_new_word(database, existing_words, overlap, fillvalue, max_tries=1000):
    # Try until we get a word not already in the wordlist.
    # Sensible only because the space of possible words is huge.
    tries = 0
    while True:
        tries += 1

        # Essentially an unfold.
        word = ""
        state = overlap*fillvalue
        while True:
            x = random.uniform(0., 1.)
            for s,more in database[state]:  # convert the distribution via CDF
                if x < s:
                    break

            word += more.rstrip(fillvalue)
            if more[-1] == fillvalue:  # end word?
                break

            state = (state + more)[-overlap:]  # NOTE: len(state + more) == seglength

        if word not in existing_words or tries >= max_tries:
            break

    existing_words.add(word)  # prevent duplicates in output

    if tries >= max_tries:
        print("WARNING: max_tries = {} exceeded, word '{}' is not new.".format(max_tries, word))

    return (word, tries)

def main():
    nout = 100     # how many words to make
    seglength = 7  # (letters) segment length for analysis
    overlap = 6    # (letters) between adjacent segments in Markov chain

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
    print("input analyzed in {:g}s ({:g} words; {:g} words/s)".format(dt_total, len(wordlist), len(wordlist) / dt_total))

    t0_total = time.time()
    database_finalize(database)
    dt_total = time.time() - t0_total
    print("distributions computed in {:g}s ({:g} entries; {:g} entries/s)".format(dt_total, len(database), len(database) / dt_total))

    # Run the generator
    out = [make_new_word(database, existing_words, overlap, fillvalue)
           for _ in range(nout)]
    print(sorted(word for word,tries in out))

    tries_data = [tries for word,tries in out]
    mean_tries = sum(tries_data) / len(tries_data)
    print("Tries made mean {}, max {}.".format(mean_tries, max(tries_data)))

if __name__ == '__main__':
    main()
