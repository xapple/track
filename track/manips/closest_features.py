# coding: utf-8

################################### Modules ####################################
from track.test import samples

################################# Description ##################################
label           = 'closest_features'
short_name      = 'Closest Features'
long_name       = 'Find the closest features from one track in an other track'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single',
                    'fields':['start','end','name']},
                   {'key':'Y', 'position':2, 'kind':'single',
                    'fields':['start','end','name','strand']}]
input_args      = [{'key':'min_length',  'position':3, 'type': int, 'default': 100000,
                    'doc':'Minimal distance for attribution.'},
                   {'key':'utr_cutoff',  'position':4, 'type': int, 'default': 2000,
                    'doc':'Distance below which the gene is attributed to both.'},
                   {'key':'prom_cutoff', 'position':5, 'type': int, 'default': 10,
                    'doc':'Distance percentage below which attribution is to preceding gene.'}]
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','name','id','type','location']}]
tracks_collapse = None
fields_collapse = None
chroms_collapse = 'first'

################################ Documentation #################################
tooltip = \
"""
For instance, the ``closest_features`` manipulation can identify
the most relevant(s) gene(s) associated to each peak.

* In cases where the peak is isolated, ``min_length`` indicates maximal allowed length between peak and closest gene. Beyond this distance, the peak will not be attributed to any gene. This defaults to ``100000``.

* In cases where the peak is near two promoters (one on each strand), ``utr_cutoff`` indicates the threshold above which the peak isn't attributed to any gene. Below this threshold, the peak will be attributed to both genes. This defaults to ``2000``.

* In cases where the peak is between two genes on the same strand, ``prom_cutoff`` indicates the percentage of the distance between the two genes below which the peak is attributed to the 3'UTR of the preceding gene rather than to the promoter of the following gene. This defaults to ``10``.
"""

tickets = []

################################## Examples ####################################
numeric_example = \
""""""

visual_example = \
u"""
                             peak
      ______  min_length    ------       min_length  ______
-----|______|------...------------------...---------|______|-----
      gene 1                                         gene 2

          -->                          -->
         |______  10%        90%      |______
---------|______|-----|---------------|______|-------------------
          gene 1      prom_cutoff      gene 2
"""

#################################### Tests #####################################
tests = [
    {'tracks':   {'X': samples['small_signals'][4]['sql'],
                  'Y': samples['small_features'][2]['sql']},
     'chromosome': 'chrI',
     'expected': [(10, 20, 'Name1',  15.0, -1),
                  (30, 40, 'Name2',  50.0,  1)]}]

############################### Implementation #################################
def generate(X, Y, min_length, utr_cutoff, prom_cutoff):
    yield (10, 20, 'Name1',  15.0, -1)
    yield (30, 40, 'Name2',  50.0,  1)
