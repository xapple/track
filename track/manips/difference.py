# coding: utf-8

################################### Modules ####################################
from track.test import samples

################################# Description ##################################
label           = 'difference'
short_name      = 'Difference'
long_name       = 'Difference (boolean XOR)'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single', 'fields':['start','end']},
                   {'key':'Y', 'position':2, 'kind':'single', 'fields':['start','end']}]
input_args      = []
input_meta      = [{'key':'l', 'position':2, 'type': int, 'kind':'chrom_len'}]
output_tracks   = [{'position':1, 'fields': ['start','end']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = 'union'

################################ Documentation #################################
tooltip = \
"""
Concatenates two tracks together and subsequently performs
the fusion manipulation on the result. Form this are removed
any regions that were present in both of the original tracks.
This is equivalent to the boolean `XOR` operation.
"""

tickets = ['https://github.com/bbcf/gMiner/issues/4']

################################## Examples ####################################
numeric_example = \
"""
X [start,end]: (0,40) (50,60)
Y [start,end]: (10,20)
R [start,end]: (0,10) (20,40) (50,60)
"""

visual_example = \
u"""
X: ───▤▤▤▤▤▤▤▤▤────────────▤▤▤▤▤▤▤──────
Y: ──────▤▤▤▤▤────▤▤▤▤▤─────────────────
R: ───▤▤──────▤───▤▤▤▤▤────▤▤▤▤▤▤▤──────
"""

#################################### Tests #####################################
tests = [
    {'tracks': {'X1': [( 5,10,'GeneA1',0.0,-1),  (20,30,'GeneA2',0.0,0), (40,50,'GeneA3',0.0,1)],
                'X2': [( 5,10,'GeneA1',0.0,-1),  (20,30,'GeneA2',0.0,0), (40,50,'GeneA3',0.0,1)],
                'Y1': [(15,20,'GeneB1',0.0,0),   (25,35,'GeneB2',0.0,0), (45,65,'GeneB3',0.0,1)],
                'Y2': [(15,20,'GeneB1',0.0,0),   (25,35,'GeneB2',0.0,0), (45,65,'GeneB3',0.0,1)]},
     'args':      {'l': 135},
     'expected':  [(  5,  10, 'GeneA1',                    0.0, 0),
                   ( 15,  25, 'GeneB1 + GeneA2 + GeneB2',  0.0, 0),
                   ( 30,  35, 'GeneB1 + GeneA2 + GeneB2',  0.0, 0),
                   ( 40,  45, 'GeneA3 + GeneB3',           0.0, 0),
                   ( 50,  65, 'GeneA3 + GeneB3',           0.0, 0)]}]
tests = []

############################### Implementation #################################
def generate(X1, X2, Y1, Y2, l):
    a = bool_and()
    o = bool_or()
    n = bool_not()
    for x in a(o(X1,Y1), n(a(X2,Y2), l)): yield x
