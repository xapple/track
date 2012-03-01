# coding: utf-8

################################### Modules ####################################
import sys
from track import common
from track.test import samples

################################# Description ##################################
label           = 'Overlap'
short_name      = 'Overlap'
long_name       = 'Pieces of overlap between two tracks (boolean AND)'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single',
                    'fields':['start','end','name','score','strand','...']},
                   {'key':'Y', 'position':2, 'kind':'single',
                    'fields':['start','end','name','score','strand','...']}]
input_args      = []
input_meta      = [{'key':'l', 'position':2, 'type': int, 'kind':'chrom_len'}]
output_tracks   = [{'position':1, 'fields': ['start','end','name','score','strand','...']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = 'intersection'

################################ Documentation #################################
tooltip = \
"""
The ``overlap`` manipulation computes the overlap between two tracks
returning new features that exactly match the overlapping zones.
This is equivalent to the boolean `AND` operation.
"""

tickets = ['https://github.com/bbcf/gMiner/issues/4']

################################## Examples ####################################
numeric_example = \
"""
X [start,end]: (0,20)
Y [start,end]: (10,30)
R [start,end]: (10,20)
"""

visual_example = \
u"""
X: ───▤▤▤▤▤▤▤▤▤─────────────────▤▤▤▤▤▤▤──────
Y: ─────────▤▤▤▤▤▤▤────▤▤▤▤▤─────────────────
R: ─────────▤▤▤──────────────────────────────
"""

#################################### Tests #####################################
tests = [
    {'tracks':     {'X': samples['small_features'][2]['sql'],
                    'Y': samples['small_features'][3]['sql']},
     'chromosome': 'chrI',
     'expected':  [( 15,  20, u'NameA + Name1',  0.1,  0),
                   ( 32,  38, u'NameB + Name2',  0.2,  1),
                   ( 95, 100, u'NameD + Name5',  0.0,  1),
                   (110, 115, u'Name6 + NameD',  0.2,  1),
                   (130, 135, u'Name7 + NameE',  0.4,  0),
                   (140, 145, u'NameF + Name7',  0.4,  0),
                   (185, 190, u'NameG + Name8',  0.2,  1),
                   (185, 195, u'NameG + Name9',  0.2,  1),
                   (210, 215, u'Name10 + NameH', 0.45-5e-17, 1),
                   (215, 220, u'NameI + Name10', 0.25, 1),
                   (235, 240, u'NameJ + Name11', 0.1,  1),
                   (250, 254, u'Name12 + NameJ', 0.15+2e-17, 1),
                   (252, 258, u'NameK + Name12', 0.25, 1),
                   (256, 260, u'NameL + Name12', 0.2,  1),
                   (270, 275, u'Name13 + NameL', 0.1,  1)]}]

############################### Implementation #################################
def make_name(a, b):
    if a and b: return a + ' + ' + b
    elif a: return a
    return b

def make_feature(a, b):
    return (max(a[0],b[0]),
            min(a[1],b[1]),
            make_name(a[2], b[2]),
            (a[3]+b[3])/2.0,
            a[4]==b[4] and b[4] or 0) + b[5:]

def generate(X, Y, l):
    """Inspired from:
    fjoin: Simple and Efficient Computation of Feature Overlap
    Journal of Computational Biology, 13(8), Oct. 2006, pp 1457-1464
    """
    # Preparation #
    sentinel = (sys.maxint, sys.maxint)
    X = common.sentinelize(X, sentinel)
    Y = common.sentinelize(Y, sentinel)
    x = X.next()
    y = Y.next()
    Wx = []
    Wy = []
    # Core loop stops when both x and y are at the sentinel
    while x[0] != sentinel or y[0] != sentinel:
        # Take the leftmost current feature and scan it against the other window
        if x[0] < y[0]:
            # Remove features from the y window that are left of x
            Wy = [f for f in Wy if f[1] > x[0]]
            # Yield new features with all overlaps of x in Wy
            for f in [f for f in Wy if f[1] > x[0] and x[1] > f[0]]: yield make_feature(x, f)
            # Put x in the window only if it is not left of y
            if x[1] >= y[0]: Wx.append(x)
            # Advance current x feature
            x = X.next()
        else:
            # Remove features from the x window that are left of y
            Wx = [f for f in Wx if f[1] > y[0]]
            # Yield new features with all overlaps of y in Wx
            for f in [f for f in Wx if f[1] > y[0] and y[1] > f[0]]: yield make_feature(y, f)
            # Put y in the window only if it is not left of x
            if y[1] >= x[0]: Wy.append(y)
            # Advance current y feature
            y = Y.next()
