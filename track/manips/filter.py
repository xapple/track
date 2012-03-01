# coding: utf-8

################################### Modules ####################################
import sys
from track import common
from track.test import samples

################################# Description ##################################
label           = 'filter'
short_name      = 'Filter'
long_name       = 'Filter features in a track by using a second track'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single', 'fields':['start','end','...']},
                   {'key':'Y', 'position':2, 'kind':'single', 'fields':['start','end']}]
input_args      = []
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','...']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = 'first'

################################ Documentation #################################
tooltip = \
"""
The ``filter`` manipulation computes the overlap of
the first track against the second stream returning only
complete features from the first track.
"""

tickets = []

################################## Examples ####################################
numeric_example = \
"""
X [start,end]: (10,20) (30,40)
Y [start,end]: (10,12) (17,22)
R [start,end]: (10,20) (30,40)
"""

visual_example = \
u"""
X: ───▤▤▤▤▤▤▤▤▤────────────▤▤▤▤▤▤▤──────
Y: ──────▤▤▤▤▤────▤▤▤▤▤─────────────────
R: ───▤▤▤▤▤▤▤▤▤─────────────────────────
"""

#################################### Tests #####################################
tests = [
    {'tracks':     {'X': samples['small_features'][2]['sql'],
                    'Y': samples['small_features'][3]['sql']},
     'chromosome': 'chrI',
     'expected':  [( 10,  20, u'Name1',  0.1, -1),
                   ( 30,  40, u'Name2',  0.2, 1),
                   ( 90, 100, u'Name5',  0.0, 1),
                   (110, 120, u'Name6',  0.4, 1),
                   (130, 150, u'Name7',  0.4, -1),
                   (180, 190, u'Name8',  0.1, 1),
                   (180, 200, u'Name9',  0.1, 1),
                   (210, 220, u'Name10', 0.2, 1),
                   (230, 240, u'Name11', 0.1, 1),
                   (250, 260, u'Name12', 0.2, 1),
                   (270, 280, u'Name13', 0.0, 1)]}]

############################### Implementation #################################
def generate(X, Y):
    sentinel = (sys.maxint, sys.maxint)
    X = common.sentinelize(X, sentinel)
    Y = common.sentinelize(Y, sentinel)
    x = X.next()
    y = Y.next()
    if x == sentinel or y == sentinel: continue_loop = False
    else:                              continue_loop = True
    while continue_loop:
        open_window  = y[0]
        close_window = y[1]
        # Extend the Y window as long as possible #
        while True:
            if y == sentinel: break
            y = Y.next()
            if y[0] > close_window: break
            if y[1] > close_window: close_window = y[1]
        # Read features from X until overshooting the Y window #
        while True:
            if x[0] >= close_window: break
            if x[1] >  open_window:  yield x
            x = X.next()
            if x == sentinel:
                continue_loop = False
                break
