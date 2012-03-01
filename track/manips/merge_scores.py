# coding: utf-8

################################### Modules ####################################
import sys
from track import common
from track.test import samples

################################# Description ##################################
label           = 'merge_scores'
short_name      = 'Merge scores'
long_name       = 'Merge scores of all signals together'
input_tracks    = [{'key':'n_tracks', 'position':1, 'kind': 'many', 'no-overlap':True,
                    'fields':['start','end','score']}]
input_args      = [{'key':'geometric', 'position':2, 'type': bool, 'default': False,
                    'doc':'Use the geometric mean instead of the arithmetic mean.'}]
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','score'], 'datatype':'signal'}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = 'union'

################################ Documentation #################################
tooltip = \
"""
The ``merge_scores`` manipulation merges N signals
using some average function. If the boolean value ``geometric``
is true, the geometric mean is used, otherwise the arithmetic
mean is used.
"""

tickets = ['https://github.com/bbcf/gMiner/issues/2']

################################## Examples ####################################
numeric_example = \
"""
X1 [start,end,score]: (10,20,50) (30,40,100)
X2 [start,end,score]: (10,12,20)
R  [start,end,score]: (10,20,40) (12,20,25) (30,40,50)
"""

visual_example = \
u"""
X1: ▁▁▁▁▁▁▁▁▁▁█████████▁▁▁▁▁▁
X2: ▁▁▁▁▁▅▅▅▅▅▅▅▅▅▅▁▁▁▁▁▁▁▁▁▁
R:  ▁▁▁▁▁▂▂▂▂▂▇▇▇▇▇▅▅▅▅▁▁▁▁▁▁
"""

#################################### Tests #####################################
tests = [
    {'tracks':   {'n_tracks': [samples['small_signals'][1]['sql'],
                               samples['small_signals'][2]['sql'],
                               samples['small_signals'][3]['sql']]},
     'args':     {'l':200},
     'chromosome': 'chrI',
     'expected': [( 0,    5,    2.0 + 0.6666666666666666),
                  ( 5,   10,    4.0),
                  ( 20,  30,   10.0),
                  ( 30,  40,   30.0),
                  ( 40,  50,   26.0 + 0.666666666666666),
                  ( 50,  60,  120.0),
                  ( 60,  68,  100.0),
                  ( 68,  70,  200.0),
                  ( 70,  80,  100.0),
                  ( 90, 110,    3.0),
                  (120, 130,   10.0)]}]

############################### Implementation #################################
def generate(n_tracks, geometric=False):
    # Get all iterators #
    sentinel = (sys.maxint, sys.maxint, 0.0)
    tracks = [common.sentinelize(x, sentinel) for x in n_tracks]
    elements = [x.next() for x in tracks]
    tracks_denom = 1.0/len(tracks)
    # Choose meaning function #
    if geometric: mean_fn = lambda x: sum(x)**tracks_denom
    else:         mean_fn = lambda x: sum(x)*tracks_denom
    # Check empty #
    for i in xrange(len(tracks)-1, -1, -1):
        if elements[i] == sentinel:
            tracks.pop(i)
            elements.pop(i)
    # Core loop #
    while tracks:
        # Find the next boundaries #
        start = min([x[0] for x in elements])
        end = min([x[0] for x in elements if x[0] > start] + [x[1] for x in elements])
        # Scores between boundaries #
        scores = [x[2] for x in elements if x[1] > start and x[0] < end]
        if scores: yield (start, end, mean_fn(scores))
        # Iterate over elements #
        for i in xrange(len(tracks)-1, -1, -1):
            # Change all starts #
            if elements[i][0] < end:
                elements[i] = (end, elements[i][1], elements[i][2])
            # Advance the elements that need to be advanced #
            if elements[i][1] <= end:
                elements[i] = tracks[i].next()
            # Pop sentinels #
            if elements[i] == sentinel:
                tracks.pop(i)
                elements.pop(i)
