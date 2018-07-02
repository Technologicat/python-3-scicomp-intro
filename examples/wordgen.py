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
    # http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
    return ("".join(letters) for letters in zip(*[word[i:] for i in range(n)]))
#    # not pythonic, but a bit faster; however, not significantly so here.
#    return [word[i:(i+n)] for i in range(len(word) - n + 1)]

# Markov chain build helper.
#
# Given ngrams from a word, and an integer 0 < k < n,
# find in this word, which (n - k) letters may follow,
# if we are given the first k letters of an ngram.
#
# Return all possibilities as a Counter (multiset).
#
def chains(ngrams, k):
    d = {}
    for s in ngrams:
        pre, suf = s[:k], s[k:]
        if pre not in d:
            d[pre] = Counter()
        d[pre][suf] += 1
    return d

# Note on padding lengths:
#
#   The state of the word generator is a string of length `overlap`,
#   initialized to overlap*fillvalue.
#
#   Each state transition produces (seglength - overlap) more letters.
#
def chains_from_word(word, seglength, overlap, fillvalue="*"):
    padded_word = "{pad1}{w}{pad2}".format(pad1=overlap*fillvalue,
                                           pad2=(seglength - overlap)*fillvalue,
                                           w=word)
    ng = ngrams(padded_word, seglength)
    return chains(ng, overlap)

# Database for state transitions. Let's do this functionally without OOP.
#
# database: dict,
#    str (length: == overlap) -> str (length: == seglength - overlap)

def database_init():
    return {}

# mutates database! (too expensive to copy, and we want mutation anyway.)
def database_update(database, chains):  # chains: as output from chains()
    for pre in chains:
        if pre not in database:
            database[pre] = chains[pre]
        else:
            database[pre].update(chains[pre])

# Convert the counters to cumulative distribution functions.
# mutates database!
def database_finalize(database):
    for pre in database:
        data = database[pre]  # the Counter listing suffixes for this prefix
        sufs = sorted(data.keys())
        n = sum(data.values())

        # compute the cumulative distribution function
        out = []
        s = 0.
        for suf in sufs[:-1]:
            s += data[suf] / n
            out.append((s, suf))
        if len(sufs):
            out.append((1., sufs[-1]))  # avoid rounding errors in last item

        # overwrite raw counts with probability data (also different format!)
        database[pre] = tuple(out)

# Given the current word (str), return the corresponding new state of the
# word generator. Used as database key, hence the name.
#
def key_from_word(word, overlap, fillvalue):
    key = word[-overlap:]   # the last `overlap` letters
    if len(key) < overlap:  # but if not long enough, left-pad by fillvalue
        key = "{}{}".format(fillvalue*(overlap - len(key)), key)
    return key

# mutates existing_words! (to prevent duplicates in output)
def make_new_word(database, existing_words, overlap, fillvalue, max_tries=1000):
    # We try until we get a word not already in the wordlist.
    #
    # This is sensible only because the number of possible words is huge
    # compared to the number of actually allocated ones.
    tries = 0
    while True:
        tries += 1

        # This is essentially an unfold.
        #
        word = ""
        key = overlap*fillvalue
        while True:
            # old trick to map the uniform distribution to a given one via the CDF.
            x = random.uniform(0., 1.)
            for p,letters in database[key]:
                if x < p:  # choose this one?
                    break
            else:
                assert False  # cannot happen

            word += letters.rstrip(fillvalue)
            key = key_from_word(word, overlap, fillvalue)
            if letters[-1] == fillvalue:  # end word?
                break

        if word not in existing_words or tries >= max_tries:
            break

    existing_words.add(word)  # prevent duplicates in output

    return (word, tries)

def main():
#    filename = "words_afew.txt"
    filename = "words_alpha.txt"  # input wordlist to analyze
    nout = 100  # how many words to make
    seglength = 6
    overlap = 4

    fillvalue = "*"

#    wordlist = ("catamaran", "adventurous")
    with open(filename, mode="rt", encoding="utf-8") as file:
        wordlist = [line.strip() for line in file]
    existing_words = set(wordlist)

    # Build the data for the Markov chains
    database = database_init()

    t0_total = time.time()
    t0 = t0_total
    for j,word in enumerate(wordlist):
        dt = time.time() - t0
        if dt > 1.:
            print("analyzing {}/{}: '{}'".format(j+1, len(wordlist), word))
            t0 = time.time()
        database_update(database,
                        chains_from_word(word, seglength, overlap, fillvalue))
    print(time.time() - t0_total)

    database_finalize(database)

    # Run the generator
    out = [make_new_word(database, existing_words, overlap, fillvalue)
           for _ in range(nout)]
    print(sorted(out))

if __name__ == '__main__':
    main()
