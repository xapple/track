# coding: utf-8

################################### Modules ####################################
import sys
from track import common

################################# Description ##################################
label           = 'window_smoothing'
short_name      = 'Window smoothing'
long_name       = 'Smooth scores with a moving window'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single', 'no-overlap':True,
                    'fields':['start','end','score']}]
input_args      = [{'key':'L', 'position':2, 'type': int, 'default': 200, 'doc':'The window radius.'}]
input_meta      = [{'key':'l', 'position':3, 'type': int, 'kind':'chrom_len'}]
output_tracks   = [{'position':1, 'fields': ['start','end','score'], 'datatype':'signal'}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = None

################################ Documentation #################################
tooltip = \
"""
Given a signal track and a window size in base pairs,
the ``windows_smoothing`` manipulation will output a new signal
track with, at each position p, the mean of the scores
in the window [p-L, p+L]. Border cases are handled by zero padding
and the signal's support is invariant.
"""

tickets = ['https://github.com/bbcf/gMiner/issues/7']

################################## Examples ####################################
numeric_example = \
""""""

visual_example = \
u"""
X: ▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁
R: ▁▁▁▁▁▁▂▄▅▇████████████▇▅▄▂▁▁▁▁▁▁▁▁
"""

#################################### Tests #####################################
tests = [
    {'tracks':   {'X': iter([(0,2,10),(2,4,20),(6,8,10)])},
     'args':     {'l':9, 'L':2},
     'expected': [(0,  1,   8.0),
                  (1,  3,  12.0),
                  (3,  5,  10.0),
                  (5,  6,   8.0),
                  (6,  9,   4.0),]}
     ,
    {'tracks':   {'X': iter([(0,2,10),(2,4,20),(6,8,10)])},
     'args':     {'l':12, 'L':2},
     'expected': [(0,  1,   8.0),
                  (1,  3,  12.0),
                  (3,  5,  10.0),
                  (5,  6,   8.0),
                  (6,  9,   4.0),
                  (9,  10,  2.0),]}]

############################### Implementation #################################
def generate(X, L, l):
    # Sentinel #
    sentinel = (sys.maxint, sys.maxint, 0.0)
    X = common.sentinelize(X, sentinel)
    # Growing and shrinking list of features around our moving window #
    F = []
    # Current position counting on nucleotides (first nucleotide is zero) #
    p = -L-2
    # Position since which the mean hasn't changed #
    same_since = -L-3
    # The current mean and the next mean #
    curt_mean = 0
    next_mean = 0
    # Multiplication factor instead of division #
    f = 1.0 / (2*L+1)
    # First feature if it exists #
    F.append(X.next())
    if F == [sentinel]: return
    # Core loop #
    while True:
        # Advance one #
        p += 1
        # Window start and stop #
        s = p-L
        e = p+L+1
        # Scores entering window #
        if F[-1][1] < e: F.append(X.next())
        if F[-1][0] < e: next_mean += F[-1][2] * f
        # Scores exiting window #
        if F[ 0][1] < s: F.pop(0)
        if F[ 0][0] < s: next_mean -= F[ 0][2] * f
        # Border condition on the left #
        if p < 0:
            curt_mean = 0
            same_since = p
            continue
        # Border condition on the right #
        if p == l:
            if curt_mean != 0: yield (same_since, p, curt_mean)
            break
        # Maybe emit a feature #
        if next_mean != curt_mean:
            if curt_mean != 0: yield (same_since, p, curt_mean)
            curt_mean  = next_mean
            same_since = p
