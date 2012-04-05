"""
This module implements the WIG serialization.
"""

# Internal modules #
from track.serialize import Serializer
from track.common import format_float

# Constants #
all_fields = ['start', 'end', 'score']

################################################################################
class SerializerWIG(Serializer):
    format = 'wig'

    def __enter__(self):
        self.file = open(self.path, 'w')
        self.indices = None
        self.previous_end = None
        self.previous_span = None
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        # Check that we have what we need #
        if not 'start' in fields: self.error("You tried to write a WIG file without a start field.")
        if not 'end' in fields:   self.error("You tried to write a WIG file without a end field.")
        if not 'score' in fields: self.error("You tried to write a WIG file without a score field.")
        # Check for the simple case  #
        if fields == tuple(all_fields): return
        # What indexes should we take #
        self.indices = [fields.index(f) for f in all_fields]

    def newTrack(self, info=None, name=None):
        if not info: info = {}
        info['type'] = 'wig'
        info['converted_by'] = __package__
        self.file.write("track " + ' '.join([k + '="' + v + '"' for k, v in info.items()]) + '\n')
        self.tracks.append(self.path)

    def newFeature(self, chrom, feature):
        # Put the fields in the right order #
        if self.indices: f = [feature[i] for i in self.indices]
        else:            f = list(feature)
        start, end, span, score = f[0], f[1], f[1]-f[0], format_float(f[2])
        # Look ahead #
        if not self.previous_end:
            self.writeFixedStep(chrom, start, end, span, score)
            return
        # If we have the same span just add the score #
        if start == self.previous_end and span == self.previous_span:
            self.file.write(score + '\n')
            self.previous_end += span
        else:
            self.writeFixedStep(chrom, start, end, span, score)

    def writeFixedStep(self, chrom, start, end, span, score):
        self.file.write("fixedStep chrom=%s start=%s span=%s\n%s\n" % (chrom, start, span, score))
        self.previous_end = end
        self.previous_span = span

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
