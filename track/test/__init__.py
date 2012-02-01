"""
Provides unittesting to the pacakge. Every format implemented should have its corresponding tests.

To run all the unitests, in the distribution directory, type::

   $ nosetests --with-doctest

The __init__ file here creates a large dictionary of different tracks found in the "samples" directory constisting mainly small validation tracks
This dictionariy is then used by the unittests themselves.
"""

# Built-in modules #
import os

################################################################################
# Tracks path #
try:
    project_path = os.path.abspath('/'.join(os.path.realpath(__file__).split('/')[:-1]) + '../../../') + '/'
    samples_path = project_path + 'samples/'
except NameError:
    samples_path = 'samples/'

# Overide with an environement variable #
if os.environ.has_key('SAMPLE_TRACKS_PATH'):
    samples_path = os.environ['SAMPLE_TRACKS_PATH']

# Ending slash #
if not samples_path.endswith('/'): samples_path += '/'

# Chromosome files #
chr_files = {
    'yeast': samples_path + 'chrmeta/yeast.chr',
    'small': samples_path + 'chrmeta/yeast.chr'
}

# Tracks collection #
samples = {
  'small_features': {
    1:            {'name':'Validation features 1', 'filename': 'features1'},
    2:            {'name':'Validation features 2', 'filename': 'features2'},
    3:            {'name':'Validation features 3', 'filename': 'features3'},
    4:            {'name':'Validation features 4', 'filename': 'features4'},
    5:            {'name':'Validation features 5', 'filename': 'features5'},
  },
  'small_signals': {
    1:            {'name':'Signal track 1',        'filename': 'scores1'},
    2:            {'name':'Signal track 2',        'filename': 'scores2'},
    3:            {'name':'Signal track 3',        'filename': 'scores3'},
    4:            {'name':'Signal track 4',        'filename': 'scores4'},
    5:            {'name':'Signal track 5',        'filename': 'scores5'},
    6:            {'name':'Signal track 6',        'filename': 'scores6'},
    7:            {'name':'Signal track 7',        'filename': 'scores7'},
  },
  'rand_features': {
    1:            {'name':'Random features 1',     'filename': 'random1'},
    2:            {'name':'Random features 2',     'filename': 'random2'},
    3:            {'name':'Random features 3',     'filename': 'random3'},
    4:            {'name':'Random features 4',     'filename': 'random4'},
  },
  'rand_signals': {
    'Pol2':       {'name':'Pol2 signal',           'filename': 'yeast_pol2'},
    'Rap1':       {'name':'Rap1 signal',           'filename': 'yeast_rap1'},
  },
  'yeast_features': {
    'All':        {'name':'All yeast genes',       'filename': 'yeast_genes'},
    'Ribi':       {'name':'Yeast Ribi genes',      'filename': 'yeast_ribi_genes'},
    'RP':         {'name':'Yeast RP genes',        'filename': 'yeast_rp_genes'},
  },
  'gff_tracks': {
    1:            {'name':'UCSC GFF example',      'filename': 'gff_test1'},
  },
  'gtf_tracks': {
    1:            {'name':'WUSTL GTF example',     'filename': 'gtf_test1'},
    'GenRep':     {'name':'GenRep saccer GTF',     'filename': 'gtf_saccer'},
  },
  'gzip_tracks': {
    1:            {'name':'Validation features 1', 'filename': 'features1.bed'},
    4:            {'name':'Validation features 4', 'filename': 'features4'},
  },

}

# Add the path for every format #
formats = ['sql', 'bed', 'wig', 'gff', 'gtf', 'bedgraph', 'bigwig', 'gzip']
for group_key, group in sorted(samples.items()):
    for track_key, track in sorted(group.items()):
        for format in formats:
            track[format] = samples_path + format + '/' + track['filename'] + '.' + format

# Per format lists #
bed_samples = samples['small_features'].values() + \
              samples['yeast_features'].values()

# Specially hard to parse tracks for testing #
if os.path.exists(samples_path):
    formats = ['bed', 'wig']
    outcomes = ['pass', 'fail']
    challanges = {}
    for format in formats:
        challanges[format] = {}
        for outcome in outcomes:
            directory = samples_path + format + '/' + 'should_' + outcome + '/'
            challanges[format][outcome] = [directory + file for file in os.listdir(directory) if file.endswith('.' + format)]

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
