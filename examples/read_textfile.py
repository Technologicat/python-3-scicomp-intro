# How to read in text files.

# File paths must be joined using os.path.join(), because the directory separator
# is / in *nix and \ in Windows. Hence, if hardcoded, *both* would be wrong.
#
# os.path.join() knows which OS Python is running on, and uses the correct
# path separator.
#
import os
filename = os.path.join("data", "utf8_text_file.txt")

# Read in the file.
#
# The with block (context manager) will automatically close the file
# when the block exits, whether the exit occurs normally or due to an exception.
#
with open(filename, "rt", encoding="utf-8") as f:
    lines = []
    for line in f:  # a text file is an iterable, where each item is a line.
        lines.append(line.strip())  # strip() removes leading and trailing whitespace, including newlines.

# Print out what we got from the file. Prepend line number.
#
for i,s in enumerate(lines):
    print(i, s, sep=': ', end='\n')
