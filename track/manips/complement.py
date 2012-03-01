# coding: utf-8

################################### Modules ####################################
from track.test import samples

################################# Description ##################################
label           = 'complement'
short_name      = 'Complement'
long_name       = 'Complement (boolean NOT)'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single', 'fields':['start','end']}]
input_args      = []
input_meta      = [{'key':'l', 'position':2, 'type': int, 'kind':'chrom_len'}]
output_tracks   = [{'position':1, 'fields': ['start','end']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = None

################################ Documentation #################################
tooltip = \
"""
The ``complement`` manipulation takes only one track
for input. The output consists of all intervals that
were not covered by a feature in the input track.
This corresponds to the boolean NOT operation.
"""

tickets = ['https://github.com/bbcf/gMiner/issues/4']

################################## Examples ####################################
numeric_example = \
"""
X [start,end]: (10,20) (30,40)
R [start,end]: ( 0,10) (20,30) (40,1000)
"""

visual_example = \
u"""
X: ──────▤▤▤▤▤─────────▤▤▤▤▤──────
R: ▤▤▤▤▤▤─────▤▤▤▤▤▤▤▤▤─────▤▤▤▤▤▤
"""

#################################### Tests #####################################
tests = [
    {'tracks':     {'X': samples['small_features'][1]['sql']},
     'chromosome': 'chrI',
     'expected':  [( 10,     20),
                   ( 30,     40),
                   ( 50,     60),
                   ( 80,     90),
                   (110,    120),
                   (135, 230208)]}]

############################### Implementation #################################
def generate(X, l):
    end = 0
    for x in X:
        if x[0] > end:
            yield (end, x[0])
            end = x[1]
        else:
            end = max(x[1], end)
    if end < l:
        yield (end, l)
