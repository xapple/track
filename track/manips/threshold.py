# coding: utf-8

################################### Modules ####################################
from track.test import samples

################################# Description ##################################
label           = 'threshold'
short_name      = 'Threshold'
long_name       = 'Apply a score threshold'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single', 'fields':['start','end','score','...']}]
input_args      = [{'key':'s', 'position':2, 'type': int, 'doc':'Score threshold.'}]
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','score','...']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = None

################################ Documentation #################################
tooltip = \
"""
Given a track ``X`` and a real number ``s``, the ``threshold``
manipulation will remove any features with a score below the ``s`` value.
"""

tickets = ['https://github.com/bbcf/gMiner/issues/3']

################################## Examples ####################################
numeric_example = \
"""
X [start,end,score]: (10,20,10) (30,40,5)
s: 8
R [start,end,score]: (10,20,10)
"""

visual_example = \
u"""
X: ▁▁▁▁▅▅▅▅▅▅▅▅▅▅▁▁▁▂▂▂▂▂▂▂▂▂▂▁▁▁▁█████████▁▁
R: ▁▁▁▁▅▅▅▅▅▅▅▅▅▅▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████████▁▁
"""

#################################### Tests #####################################
tests = [
    {'tracks':     {'X': samples['small_features'][1]['sql']},
     'chromosome': 'chrI',
     'args':       {'s': 4.0},
     'expected':  [( 0,   10,  10.0, u'Validation feature 1'),
                   (20,   30,  10.0, u'Validation feature 3'),
                   (40,   50,  10.0, u'Validation feature 6'),
                   (60,   70,  10.0, u'Validation feature 7'),
                   (70,   80,  10.0, u'Validation feature 8'),
                   (90,  100,  10.0, u'Validation feature 9'),
                   (90,  110,  10.0, u'Validation feature 10'),
                   (120, 130,  10.0, u'Validation feature 11'),
                   (125, 135,   5.0, u'Validation feature 12')]}]

############################### Implementation #################################
def generate(X, s):
    for x in X:
        if x[2] >= s: yield tuple(x)
