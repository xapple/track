"""
This module implements the BED serialization.
"""

# Internal modules #
from track.serialize import Serializer
from track.common import format_float
from track.util import int_to_strand

# Constants #
all_fields = ['start', 'end', 'name', 'score', 'strand', 'thick_start',
              'thick_end', 'item_rgb', 'block_count', 'block_sizes', 'block_starts']

################################################################################
class SerializerBED(Serializer):
    format = 'bed'

    def __enter__(self):
        self.file = open(self.path, 'w')
        self.indices = []
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        # Check that all fields are legal #
        if not all([f in all_fields for f in fields]):
            message = "You tried to write a '%s' fields to a BED file. Possible fields are: %s"
            self.error(message % (fields, all_fields))
        # Check for the simple case  #
        if all([fields[i] == all_fields[i] for i in range(len(fields))]): return
        # Find the highest ranked field #
        number_of_columns = max(all_fields.index(f) for f in fields) + 1
        # Check for availability #
        for f in all_fields[:number_of_columns]:
            if f in fields: self.indices.append(fields.index(f))
            else: self.indices.append(None)

    def newTrack(self, info=None, name=None):
        if not info: info = {}
        info['type'] = 'bed'
        info['converted_by'] = __package__
        self.file.write("track " + ' '.join([k + '="' + v + '"' for k, v in info.items()]) + '\n')
        self.tracks.append(self.path)

    def newFeature(self, chrom, feature):
        # Put the fields in the right order #
        if self.indices: line = [feature[i] if i != None else '' for i in self.indices]
        else:            line = list(feature)
        # Convert the score #
        try: line[3] = format_float(line[3])
        except IndexError: pass
        # Convert the strand #
        try: line[4] = int_to_strand(line[4])
        except IndexError: pass
        # Make sure eveything is a string #
        line = [str(f) for f in line]
        # Write one line #
        self.file.write('\t'.join([chrom] + line) + '\n')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
