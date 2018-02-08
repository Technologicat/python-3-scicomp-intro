#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anagram generator using Python's generators.

Requires a word list; get one e.g. here:

  https://github.com/dwyl/english-words

(The example uses words_alpha.txt.)

Created on Thu Feb  8 20:41:10 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

from collections import Counter

def split(n):
    """Split a (small) positive integer n to all ordered sequences of smaller positive integers that sum to n.

    Parameters:
        n: int, >= 1
            The integer to split.

    Returns:
        A generator that produces all the possible splits in sequence.
    """
    # sanity check and fail-fast
    if not isinstance(n, int):
        raise TypeError('n must be integer; got {:s}'.format(str(type(n))))
    if n < 1:
        raise ValueError('n must be positive; got {:d}'.format(n))

    # the generator object
    def _split(n):
        for k in range(1, n+1):
            m = n - k
            if m == 0:
                yield (k,)
            else:
                out = []
                for item in _split(m):
                    out.append((k,) + item)
                for term in out:
                    yield term

    return _split(n)  # instantiate the generator

def admissible_splits(n, min_component_length):
    """Return unique splits, disregarding ordering, where each component has at least a minimum length."""

    # - use a descending sort order for counts so we get longer subwords first.
    # - also convert the list returned by sorted() into a tuple.
    ordered = lambda lst: tuple(sorted(lst, reverse=True))

    # generate all possible splits. (Here the tuple() forces the generator.)
    s = tuple(split(n))

    # disregard ordering of subwords
    #  - sort to map all permutations of the same subword length combination
    #    onto a unique tuple
    #  - make a set to discard duplicates
    s = {ordered(combination) for combination in s}

    # keep only combinations where all subword lengths are >= given minimum
    s = {combination for combination in s if all(m >= min_component_length for m in combination)}

    # sort the result
    return ordered(s)

# There doesn't seem to be a ready-made operation for "fits into" for multisets.
def has(word, subword):
    """Check if word has the letters to make subword.

    Parameters:
        word: Counter
            Letters that are being anagrammed.

        subword: Counter
            Letter counts of partial anagram candidate.

    Returns:
        bool
    """
    if not isinstance(word, Counter) or not isinstance(subword, Counter):
        raise TypeError("Expected Counter instances as input, got word={:s}, subword={:s}".format(str(type(word)), str(type(subword))))
    for letter,count in subword.items():
        if letter not in word or word[letter] < count:
            return False
    return True

# for testing purposes: print(shas('category', 'cat'), shas('category', 'road'))
def shas(word, subword):
    """Like "has", but input as strings, and returns remaining letters (can be empty) or False."""
    word    = Counter(word)
    subword = Counter(subword)
    if has(word, subword):
        # Counters can be subtracted, but a resulting count of <= 0
        # automatically removes that element from the result.
        #
        # https://docs.python.org/3/library/collections.html#collections.Counter
        # https://stackoverflow.com/a/10176311
        return "".join(count*letter for letter,count in (word - subword).items())
    return False

# slower than without the binary cache - even the fast Python 3 pickle is slow for this
#import os
#import pickle
#class WordList:
#    def __init__(self, filename):
#        data = None
#        cache_filename = "{:s}.cache".format(filename)
#        try:
#            with open(cache_filename, 'rb') as infile:
#                data = pickle.load(infile)
#                _,lst,by_length = data
#        except IOError:
#            pass
#
#        if data is None:
#            with open(filename, mode="rt", encoding="utf-8") as file:
#                lst = [line.strip() for line in file]
#            # This takes most of the initialization time.
#            by_length = {}  # length: list of words
#            for word in lst:
#                l = len(word)
#                if l not in by_length:
#                    by_length[l] = []
#                by_length[l].append((word,Counter(word)))
#            data = (filename, lst, by_length)
#            with open(cache_filename, 'wb') as outfile:
#                pickle.dump(data, outfile, protocol=pickle.HIGHEST_PROTOCOL)
#
#        self.lst = lst
#        self.by_length = by_length

class WordList:
    def __init__(self, filename):
        with open(filename, mode="rt", encoding="utf-8") as file:
            lst = [line.strip() for line in file]

        # This takes most of the initialization time.
        by_length = {}  # length: list of words
        for word in lst:
            l = len(word)
            if l not in by_length:
                by_length[l] = []
            by_length[l].append((word,Counter(word)))

        self.lst = lst
        self.by_length = by_length

def anagrams(word, wordlist, min_component_length=1):
    letters = Counter(word)
    words_by_length = wordlist.by_length  # "eliminate dot"; faster access
    ordered = lambda lst: tuple(sorted(lst))  # use ascending lexicographical order
    out = []
    for the_split in admissible_splits(len(word), min_component_length):
        if not all((length in words_by_length) for length in the_split):
            continue

        # Generator that returns words of the given length that fit into
        # the given letters.
        #
        def build_component(letters, length):
            for component,component_letters in words_by_length[length]:
                if has(letters, component_letters):
                    yield component, letters - component_letters

        # The magic of generators: we yield only successful anagrams!
        #
        # Because build_component yields only valid candidates, and we iterate
        # over the set of yielded results, failures are discarded automatically.
        #
        # Hence we need no explicit backtracking for dead-end branches that
        # fail to use up all the letters of the input.
        #
        def comb(letters, lengths):  # remaining letters, remaining component lengths
            m,*rest = lengths
            for component,remaining_letters in build_component(letters, m):
                if not len(rest):
                    yield (component,)
                else:
                    out = []
                    for item in comb(remaining_letters, rest):
                        out.append((component,) + item)
                    for term in out:
                        yield term

        # Generate the anagrams
        results = comb(letters, the_split)

        # Disregard word order, discard duplicates
        results = {ordered(result) for result in results}

        # Sort the set of results itself
        results = ordered(results)

        out.extend(results)
    return out

def main():
    w = WordList("words_alpha.txt")

    # statistics: count of words by length
    for l in sorted(w.by_length.keys()):
        print(l, len(w.by_length[l]))

    result = anagrams(word='category', wordlist=w, min_component_length=4)
    print(result)

if __name__ == '__main__':
    main()

#print(shas('banana', 'aaa'))
#print(shas('banana', 'ann'))
#print(shas('banana', 'car'))
#print(shas('banana', 'banana'))
