# coding: utf-8

################################### Modules ####################################
import sys
from track import common
from track.test import samples

################################# Description ##################################
label           = 'mean_score_by_feature'
short_name      = 'Mean score by feature'
long_name       = 'Mean score of the signal in every feature'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single', 'no-overlap': True,
                    'fields':['start','end','score']},
                   {'key':'Y', 'position':2, 'kind':'single',
                    'fields':['start','end','score','...']}]
input_args      = []
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','score','...']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = 'last'

################################ Documentation #################################
tooltip = \
"""
Given a signal track ``X`` and a feature track ``Y``,
the ``mean_score_by_feature`` manipulation computes the mean of scores
of every of ``Y``'s features in ``X``. The output consists of a feature track
similar to ``Y`` but with a new score value property for every feature.
"""

tickets = ['https://github.com/bbcf/gMiner/issues/6']

################################## Examples ####################################
numeric_example = \
"""
X [start,end,score]: (10,20,999)   (30,40,9999)
Y [start,end,score]: (10,12,5)     (17,22,500)
R [start,end,score]: (10,20,151)   (30,40,0)
"""

visual_example = \
u"""
X: ──────▤▤▤▤▤▤▤▤▤▤──────────────▤▤▤▤▤▤▤▤▤▤──────
Y: ▁▁▁▁▁▁▁▁▁▁▁█████████▁▁▁▁▁▁▁▁▁▁██████████▁▁▁▁▁▁
R: ▁▁▁▁▁▁▅▅▅▅▅▅▅▅▅▅▁▁▁▁▁▁▁▁▁▁▁▁▁▁██████████▁▁▁▁▁▁
"""

#################################### Tests #####################################
tests = [
    {'tracks':   {'X': iter([(10,12,5),   (17,22,500)]),
                  'Y': iter([(10,20),     (30,40)    ])},
     'expected':            [(10,20,151), (30,40,0)]}
     ,
    {'tracks':   {'X': samples['small_signals'][4]['sql'],
                  'Y': samples['small_features'][2]['sql']},
     'expected': [('chrI', 10,   20, 15.0, u'Name1',  -1),
                  ('chrI', 30,   40, 50.0, u'Name2',   1),
                  ('chrI', 50,   60, 30.0, u'Name3',   1),
                  ('chrI', 70,   80, 25.0, u'Name4',   1),
                  ('chrI', 90,  100,  8.0, u'Name5',   1),
                  ('chrI', 110, 120,  0.0, u'Name6',   1),
                  ('chrI', 130, 150,  1.0, u'Name7',  -1),
                  ('chrI', 180, 190,  5.0, u'Name8',   1),
                  ('chrI', 180, 200,  8.0, u'Name9',   1),
                  ('chrI', 210, 220,  0.0, u'Name10',  1),
                  ('chrI', 230, 240,  0.0, u'Name11',  1),
                  ('chrI', 250, 260,  0.0, u'Name12',  1),
                  ('chrI', 270, 280,  0.0, u'Name13',  1),
                  ('chrI', 290, 300,  0.0, u'Name14', -1)]}]

############################### Implementation #################################
def generate(X, Y):
    # Sentinel #
    sentinel = (sys.maxint, sys.maxint, 0.0)
    X = common.sentinelize(X, sentinel)
    # Growing and shrinking list of features in X #
    F = [(-sys.maxint, -sys.maxint, 0.0)]
    # --- Core loop --- #
    for y in Y:
        # Check that we have all the scores necessary #
        xnext = F[-1]
        while xnext[0] < y[1]:
            xnext = X.next()
            if xnext[1] > y[0]: F.append(xnext)
        # Throw away the scores that are not needed anymore #
        n = 0
        while F[n][1] <= y[0]:
            n+=1
        F = F[n:]
        # Compute the average #
        score = 0.0
        for f in F:
            if y[1] <= f[0]: continue
            if f[0] <  y[0]: start = y[0]
            else:            start = f[0]
            if y[1] <  f[1]: end   = y[1]
            else:            end   = f[1]
            score += (end-start) * f[2]
        # Emit a feature #
        yield y[0:2]+(score/(y[1]-y[0]),)+y[3:]
