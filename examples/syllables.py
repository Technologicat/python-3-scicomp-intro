#!/usr/bin/env python

import collections
import contextlib

import numpy as np

import libvoikko

@contextlib.contextmanager
def VoikkoSession():
    voikko = libvoikko.Voikko("fi")
    try:
        yield voikko
    finally:
        voikko.terminate()

def main():
    print("Analyzing...")

    c = collections.Counter()
    with open("kotus_sanat.txt", "rt") as wordlist:
        with VoikkoSession() as voikko:
            for word in wordlist:
                word = word.strip().lower()
                hyphenated = voikko.hyphenate(word)
                syllables = hyphenated.split("-")
                c.update(syllables)

    # Drop blank entries
    c = {k: v for k, v in c.items() if len(k) > 0}

    # How many times does each syllable appear?
    values = np.array(list(c.values()))
    print(f"Total syllables collected: {np.sum(values)}")
    print(f"Unique syllables collected: {len(c)}")

    # Occurrences statistics
    occurrences_median = np.median(values)
    print()
    print("Occurrences of each unique syllable:")
    print(f"    min {np.min(values)}, max {np.max(values)}, mean {np.mean(values):0.6g}, median {occurrences_median}, stdev {np.std(values):0.6g}")

    # Syllable length statistics
    lens = np.array(list(len(k) for k in c.keys()))
    lens_median = np.median(lens)
    print("Length of each unique syllable:")
    print(f"    min {np.min(lens)}, max {np.max(lens)}, mean {np.mean(lens):0.6g}, median {lens_median}, stdev {np.std(lens):0.6g}")

    # Get a usable list of most common syllables for word games
    occurrences_cutoff = 500
    result = {k: v for k, v in c.items() if len(k) <= lens_median and v > occurrences_cutoff}
    print(f"All syllables of at most median length, occurring at least {occurrences_cutoff} times: {len(result)}")
    print(dict(sorted(result.items(), key=lambda x: -x[1])))
    print("The same syllables, in alphabetical order:")
    print(sorted(result.keys()))

if __name__ == '__main__':
    main()
