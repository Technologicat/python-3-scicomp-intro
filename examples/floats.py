# Based on: University of Illinois, CS 357, spring 2017
# https://relate.cs.illinois.edu/course/cs357-s17/file-version/
#     66922aa3735332d7fb31c9fd9e8f7dde2fda1b37/
#     demos/upload/fp/Density%20of%20Floating%20Point%20Numbers.html

import matplotlib.pyplot as plt

# Illustration; see sys.float_info for real-world values.
mant_dig = 4
min_exp  = -3
max_exp  = 4

floats = []
for k in range(min_exp, max_exp+1):
    for i in range(2**mant_dig):
        mantissa = 1 + i/2**mant_dig 
        floats.append(mantissa * 2**k)

plt.figure(1, figsize=(5,2))
plt.clf()

# Show where exactly representable numbers in this floating point system are
for x in floats:
    plt.axvline(x)

# https://stackoverflow.com/questions/12998430/remove-xticks-in-a-matplotlib-plot
plt.tick_params(
    axis='y',          # changes apply to the y-axis
    which='both',      # both major and minor ticks are affected
    left='off',        # ticks along the left edge are off
    right='off',       # ticks along the right edge are off
    labelleft='off')   # labels along the left edge are off
