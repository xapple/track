# coding: utf-8

################################### Modules ####################################
from track.test import samples

################################# Description ##################################
label           = 'fusion'
short_name      = 'Fusion'
long_name       = 'Fuses features that are adjacent or overlapping in a track'
input_tracks    = [{'key':'X', 'position':1, 'kind': 'single',
                    'fields':['start','end','name','score','strand']}]
input_args      = []
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','name','score','strand']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = None

################################ Documentation #################################
tooltip = \
"""
The ``fusion`` manipulation will combine any features in a track that
are adjacent to one another or overlapping each other into a single
feature. The strand attribute will be conserved only if all features
that are being merged have the same strand. The score attribute will
be the sum of all the scores.
"""

tickets = []

################################## Examples ####################################
numeric_example = \
"""
X1 [start,end]: (10,20) (20,30)
R  [start,end]: (10,30)
"""

visual_example = \
u"""
X: ──────▤▤▤▤▤─────────▤▤▤▤▤──────
           ▤▤▤▤▤▤▤▤▤
R: ──────▤▤▤▤▤▤▤▤▤▤▤───▤▤▤▤▤──────
"""

#################################### Tests #####################################
tests = [
    {'tracks':     {'X': samples['small_signals'][4]['sql']},
     'chromosome': 'chrI',
     'expected': [( 10,  20, u'',   30.0, 0),
                  ( 25,  35, u'',  100.0, 0),
                  ( 45,  65, u'',   60.0, 0),
                  ( 72,  77, u'',   50.0, 0),
                  ( 85, 105, u'',    8.0, 0),
                  (120, 122, u'', 9000.0, 0),
                  (130, 131, u'',   20.0, 0),
                  (180, 183, u'',   10.0, 0),
                  (188, 193, u'',   10.0, 0),
                  (198, 200, u'',   40.0, 0)]}
     ,
    #{'tracks':   {'X': [(0,5),(5,7)]},
    #'expected': [(0,7,'',0.0,0)]},
    ]

############################### Implementation #################################
def generate(X):
    # Setup #
    for x in X: break
    if 'x' not in locals(): return
    # Core loop #
    for y in X:
        if y[0] <= x[1]:
            x = list(x)
            x[1] = max(x[1], y[1])
            # Name #
            if x[2] and y[2]: x[2] = x[2] + ' + ' + y[2]
            else: x[2] = x[2] or y[2]
            # Score #
            x[3] = x[3] + y[3]
            # Strand #
            x[4] = x[4] == y[4] and x[4] or 0
        else:
            yield tuple(x)
            x = y
    # Last feature #
    yield tuple(x)
