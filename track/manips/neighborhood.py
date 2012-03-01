# coding: utf-8

################################### Modules ####################################
import sys
from track.test import samples

################################# Description ##################################
label           = 'neighborhood'
short_name      = 'Neighborhood regions'
long_name       = 'Compute neighborhood regions upstream and downstream of features.'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single', 'fields':['start','end','...']}]
input_args      = [{'key':'before_start', 'position':3, 'type': int, 'default': 0,
                    'doc':'Base pairs before the feature start.'},
                   {'key':'after_end',    'position':4, 'type': int, 'default': 0,
                    'doc':'Base pairs after the feature end.'},
                   {'key':'after_start',  'position':5, 'type': int, 'default': 0,
                    'doc':'Base pairs after the feature start.'},
                   {'key':'before_end',   'position':6, 'type': int, 'default': 0,
                    'doc':'Base pairs before the feature end.'},
                   {'key':'on_strand', 'position':7, 'type': bool, 'default': False,
                    'doc':'Features on the negative strand can be inverted.'},]
input_meta      = [{'key':'l', 'position':2, 'type': int, 'kind':'chrom_len'}]
output_tracks   = [{'position':1, 'fields': ['start','end','...']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = None

################################ Documentation #################################
tooltip = \
"""
Given a stream of features and four integers ``before_start``, ``after_end``,
``after_start`` and ``before_end``, this manipulation will output,
for every feature in the input stream, one or two features
in the neighborhood of the original feature.

   * Only ``before_start`` and ``after_end`` are given::

         (start, end, ...) -> (start+before_start, end+after_end, ...)

   * Only ``before_start`` and ``after_start`` are given::

         (start, end, ...) -> (start+before_start, start+after_start, ...)

   * Only ``after_end`` and ``before_end`` are given::

         (start, end, ...) -> (end+before_end, end+after_end, ...)

   * If all four parameters are given, a pair of features is outputted::

         (start, end, ...) -> (start+before_start, start+after_start, ...)
                              (end+before_end, end+after_end, ...)

   * If the boolean parameter ``on_strand`` is set to True,
     features on the negative strand are inverted as such::

         (start, end, ...) -> (start-after_end, start-before_end, ...)
                              (end-after_start, end-before_start, ...)
"""

tickets = ['https://github.com/bbcf/gMiner/issues/1']

################################## Examples ####################################
numeric_example = \
"""
X [start,end]: (10,20)
R [start,end]: (5,8) (22,25)
"""

visual_example = \
u"""
X: ──────────▤▤▤▤▤▤▤▤▤──────────────
R: ────▤▤▤▤─────────────▤▤▤▤────────
"""

#################################### Tests #####################################
tests = [
    {'tracks':     {'X': samples['small_features'][1]['sql']},
     'chromosome': 'chrI',
     'args':       {'l': 135, 'before_start':-2, 'after_end':2},
     'expected':  [( 0,   12,  u'Validation feature 1',  10.0),
                   ( 0,   10,  u'Validation feature 2',   0.0),
                   (18,   32,  u'Validation feature 3',  10.0),
                   (23,   32,  u'Validation feature 4',   0.0),
                   (38,   47,  u'Validation feature 5',   0.0),
                   (38,   52,  u'Validation feature 6',  10.0),
                   (58,   72,  u'Validation feature 7',  10.0),
                   (68,   82,  u'Validation feature 8',  10.0),
                   (88,  102,  u'Validation feature 9',  10.0),
                   (88,  112,  u'Validation feature 10', 10.0),
                   (118, 132,  u'Validation feature 11', 10.0),
                   (123, 137,  u'Validation feature 12',  5.0)]}]

############################### Implementation #################################
def bounded(X, min_bound=0, max_bound=sys.maxint):
    for x in X:
        if not x[1] < min_bound and not x[0] > max_bound and x[0] < x[1]:
            yield (max(x[0],min_bound), min(x[1],max_bound)) + x[2:]

def neighborhood(X, l, before_start=0, after_end=0, after_start=0, before_end=0, on_strand=False):
    if before_start and after_start:
        if before_start > after_start:
            raise Exception("'before_start' cannot be larger than 'after_start'")
    if before_end and after_end:
        if before_end > after_end:
            raise Exception("before_end cannot be larger than 'after_end'")
    if not on_strand:
        if before_start and after_end and after_start and before_end:
            for x in X:
                yield (x[0]+before_start, x[0]+after_start) + x[2:]
                yield (x[1]+before_end,   x[1]+after_end) + x[2:]
        if before_start and after_start:
            for x in X: yield (x[0]+before_start, x[0]+after_start)  + x[2:]
        if before_end and after_end:
            for x in X: yield (x[1]+before_end,   x[1]+after_end)    + x[2:]
        if before_start and after_end:
            for x in X: yield (x[0]+before_start, x[1]+after_end)    + x[2:]
    else:
        if before_start and after_end and after_start and before_end:
            for x in X:
                yield (x[0]-after_end,   x[0]-before_end) + x[2:]
                yield (x[1]-after_start, x[1]-before_start) + x[2:]
        if before_start and after_start:
            for x in X: yield (x[1]-after_start,  x[1]-before_start) + x[2:]
        if after_end and before_end:
            for x in X: yield (x[0]-after_end,    x[0]-before_end) + x[2:]
        if before_start and after_end:
            for x in X: yield (x[0]-after_end,    x[1]-before_start) + x[2:]

def generate(X, l, **kwargs):
    return bounded(neighborhood(X, l, **kwargs), 0, l)
