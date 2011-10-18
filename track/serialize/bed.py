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
            if fields[i] != all_fields[i]:
                try:
                    self.indices = [all_fields.index(f) for f in fields]
                except ValueError:
                    message = "You tried to write a '%s' field to a BED file. Possible fields are: %s"
                    self.error(message % (f, all_fields))
                break

    def newTrack(self, info=None, name=None):
        if not info: info = {}
        info['type'] = 'bed'
        info['converted_by'] = __package__
        self.file.write("track " + ' '.join([k + '="' + v + '"' for k, v in info.items()]) + '\n')

    def newFeature(self, chrom, feature):
        # Make sure eveything is a string #
        feature = [str(f) for f in feature]
        # Put the fields in the right order #
        if self.indices: feature = [feature[i] for i in self.indices]
        # Write on line #
        self.file.write('\t'.join([chrom] + feature) + '\n')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
