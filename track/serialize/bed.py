"""
This module implements the bed serialization.
"""

# Internal modules #
from track.serialize import Serializer

# Constants #
all_fields = ['start', 'end', 'name', 'score', 'strand', 'thick_start',
              'thick_end', 'item_rgb', 'block_count', 'block_sizes', 'block_starts']

################################################################################
class SerializerBED(Serializer):
    def __enter__(self):
        self.file = open(self.path, 'w')
        self.indices = None
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        for i in range(len(fields)):
            if fields[i] != all_fields[i]: break
        else:
            self.indices = [feature[i] for i in self.indices]

    def newTrack(self, name=None, info=None):
        info['type'] = 'bed'
        info['converted_by'] = __package__
        self.file.write("track " + ' '.join([k + '="' + v + '"' for k, v in info.items()]) + '\n')

    def newFeature(self, chrom, feature):
        if self.indices: feature = [feature[i] for i in self.indices]
        self.file.write('\t'.join([chrom] + feature) + '\n')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
