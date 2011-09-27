"""
A script that can regenerate the SQL tracks from their text version as well as the binary tracks.
"""

# Genreral Modules #
import os, subprocess

# Specific module #
from track import load
from track.track_random import TrackRandom
from track.common import terminal_colors
from track.track_collection import track_collections, tracks_path, yeast_chr_file

# Variables #
chrsuffix = 'Awfully super extra long chromosome denomination string '

# Same randomness #
import random
random.seed(0)

###########################################################################
# Create tracks #
def create_tracks():
    for col_name, col in sorted(track_collections.items()):
        if col_name in ['Binary', 'Random', 'Peaks', 'Special']: continue
        for track_num, d in sorted(col.items()):
            print terminal_colors['txtylw'] + "Creating track '" + d['name'] + "'" + terminal_colors['end']
            if os.path.exists(d['path_sql']): os.remove(d['path_sql'])
            with load(d['path'], chrmeta = yeast_chr_file) as t:
                t.convert(d['path_sql'])

# Random tracks #
def create_random():
    for track_num, d in sorted(track_collections['Random'].items()):
        print terminal_colors['txtylw'] + "Creating track '" + d['name'] + "'" + terminal_colors['end']
        if os.path.exists(d['path_sql']): os.remove(d['path_sql'])
        with TrackRandom('/dev/null', 'rand', 'Test random track ' + str(track_num)) as t:
            t.size = 1000.0*(float(track_num)/2.0)
            t.export(d['path_sql'])

# Special bigWig tracks #
def create_binary():
    for track_num, d in sorted(track_collections['Binary'].items()):
        print terminal_colors['txtylw'] + "Creating track '" + d['name'] + "'" + terminal_colors['end']
        bedgraph_path = track_collections['Signals'][track_num]['path']
        proc = subprocess.Popen(['bedGraphToBigWig', bedgraph_path, yeast_chr_file, d['path']], stderr = subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if stderr: raise Exception("The tool bedGraphToBigWig exited with message: " + '"' + stderr.strip('\n') + '"')

# Special wig tracks #
def create_signals():
    from track.formats.wig import random_track
    # Pol2
    print terminal_colors['txtylw'] + "Creating track 'Pol2'" + terminal_colors['end']
    random.seed(0)
    if os.path.exists(tracks_path + 'quan/wig/pol2.wig'): os.remove(tracks_path + 'quan/wig/pol2.wig')
    with open(tracks_path + 'quan/wig/pol2.wig', 'w') as file: file.writelines(random_track('fixed'))
    if os.path.exists(tracks_path + 'quan/sql/pol2.sql'): os.remove(tracks_path + 'quan/sql/pol2.sql')
    with load(tracks_path + 'quan/wig/pol2.wig', chrmeta = yeast_chr_file) as t: t.convert(tracks_path + 'quan/sql/pol2.sql')
    # Rap1
    print terminal_colors['txtylw'] + "Creating track 'Rap1'" + terminal_colors['end']
    random.seed(0)
    if os.path.exists(tracks_path + 'quan/wig/rap1.wig'): os.remove(tracks_path + 'quan/wig/rap1.wig')
    with open(tracks_path + 'quan/wig/rap1.wig', 'w') as file: file.writelines(random_track('variable'))
    if os.path.exists(tracks_path + 'quan/sql/rap1.sql'): os.remove(tracks_path + 'quan/sql/rap1.sql')
    with load(tracks_path + 'quan/wig/rap1.wig', chrmeta = yeast_chr_file) as t: t.convert(tracks_path + 'quan/sql/rap1.sql')
