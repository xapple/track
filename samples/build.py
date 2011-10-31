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
collection_conversion =  {'small_features':     {'from':'bed', 'to':'sql', 'assembly':'sacCer2'},
                          'yeast_features':     {'from':'bed', 'to':'sql', 'assembly':'sacCer2'},
                          'small_signals':      {'from':'wig', 'to':'sql', 'assembly':'sacCer2'},
                          'rand_signals':       {'from':'wig', 'to':'sql', 'assembly':'sacCer2'},
                          'gff_tracks':         {'from':'gff', 'to':'sql', 'assembly':'sacCer2'},
                          'gtf_tracks':         {'from':'gtf', 'to':'sql', 'assembly':'sacCer2'},
                          }
# Same randomness #
import random
random.seed(0)

###########################################################################
# Create tracks #
def create_tracks():
    for collection, conversion_info in sorted(collection_conversion.items()):
        for track_name, track_info in sorted(samples[collection].items()):
            print Color.ylw + "Creating track '" + track_info['name'] + "'" + Color.end
            from_path = track_info[conversion_info['from']]
            to_path =   track_info[conversion_info['to']]
            if os.path.exists(to_path): os.remove(to_path)
            track.convert(from_path, to_path)
            with track.load(to_path) as t:
                t.assembly = conversion_info['assembly']

# Special binary tracks #
def create_binary():
    for track_num, d in sorted(track_collections['Binary'].items()):
        print Color.ylw + "Creating track '" + d['name'] + "'" + Color.end
        bedgraph_path = track_collections['Signals'][track_num]['path']
        proc = subprocess.Popen(['bedGraphToBigWig', bedgraph_path, yeast_chr_file, d['path']], stderr = subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if stderr: raise Exception("The tool bedGraphToBigWig exited with message: " + '"' + stderr.strip('\n') + '"')
