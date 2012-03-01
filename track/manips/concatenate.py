# coding: utf-8

################################### Modules ####################################
import sys
from track import common
from track.test import samples
from operator import itemgetter

################################# Description ##################################
label           = 'concatenate'
short_name      = 'Concatenate'
long_name       = 'Concatenate N tracks together'
input_tracks    = [{'key':'n_tracks', 'position':1, 'kind':'many', 'fields':['start','end','...']}]
input_args      = []
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','...']}]
tracks_collapse = None
fields_collapse = 'union'
chroms_collapse = 'union'

################################ Documentation #################################
tooltip = \
"""
The ``concatenate`` manipulation takes only one track
for input. The output consists of all intervals that
were not covered by a feature in the input track.
"""

tickets = []

################################## Examples ####################################
numeric_example = \
"""
X [start,end]: (0,20)
Y [start,end]: (10,30)
R [start,end]: (0,20) (10,30)
"""

visual_example = \
u"""
X: ───▤▤▤▤▤▤▤▤▤────────────▤▤▤▤▤▤▤──────
Y: ──────▤▤▤▤▤────▤▤▤▤▤─────────────────
R: ───▤▤▤▤▤▤▤▤▤───▤▤▤▤▤────▤▤▤▤▤▤▤──────
         ▤▤▤▤▤
"""

#################################### Tests #####################################
tests = [
    {'tracks':   {'n_tracks': [iter([(0,10),(0,10),(5,10)]),
                               iter([(0,5),(0,12),(5,8)])]},
     'expected': [(0,5),(0,10),(0,10),(0,12),(5,8),(5,10)]}
    ,
    {'tracks':   {'n_tracks': [samples['small_features'][1]['sql'],
                               samples['small_features'][4]['sql']]},
     'chromosome': 'chrI',
     'expected': [( 0,   10, u'Validation feature 1',  10.0, 0),
                  ( 2,    8, u'Validation feature 2',   0.0, 0),
                  (10,   20, u'Lorem',                  1.0, 1),
                  (20,   30, u'Validation feature 3',  10.0, 0),
                  (25,   30, u'Validation feature 4',   0.0, 0),
                  (30,   40, u'Ipsum',                  2.0, 1),
                  (40,   45, u'Validation feature 5',   0.0, 0),
                  (40,   50, u'Validation feature 6',  10.0, 0),
                  (60,   70, u'Validation feature 7',  10.0, 0),
                  (70,   80, u'Validation feature 8',  10.0, 0),
                  (90,  100, u'Validation feature 9',  10.0, 0),
                  (90,  110, u'Validation feature 10', 10.0, 0),
                  (120, 130, u'Validation feature 11', 10.0, 0),
                  (125, 135, u'Validation feature 12',  5.0, 0)]}]

############################### Implementation #################################
def generate(n_tracks):
    # Get all iterators #
    sentinel = (sys.maxint, sys.maxint, 0.0)
    tracks   = [common.sentinelize(x, sentinel) for x in n_tracks]
    features = range(len(tracks))
    # Advance feature #
    def advance(i):
        features[i] = tracks[i].next()
        if features[i] == sentinel:
            tracks.pop(i)
            features.pop(i)
    # Find lowest feature #
    def get_lowest_feature():
        i = min(enumerate([(f[0],f[1]) for f in features]), key=itemgetter(1))[0]
        return i, features[i]
    # Core loop #
    for i in xrange(len(tracks)-1, -1, -1): advance(i)
    while tracks:
        i,f = get_lowest_feature()
        yield f
        advance(i)
