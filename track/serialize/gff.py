"""
This module implements the GFF serialization.
"""

# Internal modules #
from track.serialize import Serializer
from track.common import format_float
from track.util import int_to_strand

# Constants #
all_fields = ['source', 'name', 'start', 'end', 'score', 'strand', 'frame', 'attributes']
defaults   = ['.', '.', -1, -1, 0.0, '.', '.', '.']

################################################################################
class SerializerGFF(Serializer):
    format = 'gff'

    def __enter__(self):
        self.file = open(self.path, 'w')
        self.indices = None
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        self.indices = []
        for f in all_fields:
            try: self.indices.append(fields.index(f))
            except ValueError: self.indices.append(-1)

    def newTrack(self, info=None, name=None):
        if not info: info = {}
        info['type'] = 'gff'
        info['converted_by'] = __package__
        self.file.write("track " + ' '.join([k + '="' + v + '"' for k, v in info.items()]) + '\n')
        self.tracks.append(self.path)

    def newFeature(self, chrom, feature):
        # Put the fields in the right order #
        line = range(len(all_fields))
        for n,i in enumerate(self.indices):
            if i == -1: line[n] = defaults[n]
            else:       line[n] = feature[i]
        # Convert the score #
        line[4] = format_float(line[4])
        # Convert the strand #
        line[5] = int_to_strand(line[5])
        # Convert the frame #
        if line[6] == '' or line[6] == None: line[6] = '.'
        # Make sure eveything is a string #
        line = [str(f) for f in line]
        # Write one line #
        self.file.write('\t'.join([chrom] + line) + '\n')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
