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
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        if not 'score' in fields: self.error("You tried to write a WIG files without a score field.")
        for i in range(len(fields)):
            if fields[i] != all_fields[i]:
                try:
                    self.indices = [all_fields.index(f) for f in fields]
                except ValueError:
                    message = "You tried to write a '%s' field to a WIG file. Possible fields are: %s"
                    self.error(message % (f, all_fields))
                break

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
        # Convert the score #
        try: f[2] = format_float(f[2])
        except IndexError: pass
        # Write one line #
        self.file.write("fixedStep chrom=%s start=%s span=%s\n%s\n" % (chrom,f[0],f[1]-f[0],f[2]))

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
