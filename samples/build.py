"""
A script that can regenerate the SQL tracks from their text version as well as the binary tracks.
"""

# Built-in modules #
import sys, os, subprocess

# Path #
sys.path.insert(0, os.path.abspath('../'))

# Internal modules #
import track
from track.common import Color
from track.test import samples

# Dictionaries #
collection_conversion =  {'small_features':     {'from':'bed',      'to':'sql',      'assembly':'sacCer2'},
                          'yeast_features':     {'from':'bed',      'to':'sql',      'assembly':'sacCer2'},
                          'small_signals':      {'from':'wig',      'to':'sql',      'assembly':'sacCer2'},
                          'small_signals':      {'from':'sql',      'to':'bedGraph', 'assembly':'sacCer2'},
                          'small_signals':      {'from':'bedGraph', 'to':'bigwig',   'assembly':'sacCer2'},
                          'rand_signals':       {'from':'wig',      'to':'sql',      'assembly':'sacCer2'},
                          'gff_tracks':         {'from':'gff',      'to':'sql',      'assembly':'sacCer2'},
                          'gtf_tracks':         {'from':'gtf',      'to':'sql',      'assembly':'sacCer2'},
                          'bedgraph_tracks':    {'from':'bedgraph', 'to':'sql',      'assembly':'sacCer2'},
                          'bigwig_tracks':      {'from':'bigwig',   'to':'sql',      'assembly':'sacCer2'},
                          }
# Same randomness #
import random
random.seed(0)

###########################################################################
def create_tracks():
    for collection, conversion_info in sorted(collection_conversion.items()):
        for track_name, track_info in sorted(samples[collection].items()):
            print Color.ylw + "Creating track '" + track_info['name'] + "'" + Color.end
            from_path = track_info[conversion_info['from']]
            to_path =   track_info[conversion_info['to']]
            if os.path.exists(to_path): os.remove(to_path)
            track.convert(from_path, to_path, assembly = conversion_info['assembly'])
