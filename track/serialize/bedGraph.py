"""
This module implements the bedGraph serialization.
"""

# Internal modules #
from track.serialize import Serializer
from track.common import format_float

# Constants #
all_fields = ['start', 'end', 'score']

################################################################################
class SerializerBedGraph(Serializer):
    def __enter__(self):
        self.file = open(self.path, 'w')
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        self.indices = []
        for f in all_fields:
            try:
                self.indices.append(fields.index(f))
            except ValueError:
                message = "You tried to write a bedGraph file without a '%s' field. Required fields are: %s"
                self.error(message % (f, all_fields))

    def newTrack(self, info=None, name=None):
        if not info: info = {}
        info['type'] = 'bedGraph'
        info['converted_by'] = __package__
        self.file.write("track " + ' '.join([k + '="' + v + '"' for k, v in info.items()]) + '\n')

    def newFeature(self, chrom, feature):
        # Put the fields in the right order #
        line = [feature[i] for i in self.indices]
        # Convert the score #
        line[2] = format_float(line[3])
        # Make sure eveything is a string #
        line = [str(f) for f in line]
        # Write one line #
        self.file.write('\t'.join([chrom] + line) + '\n')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
