"""
This module implements the sql serialization.
"""

# Internal modules #
import track
from track.seralize import Serializer
from track.common import make_file_names

################################################################################
class SerializerSQL(Serializer):
    def __enter__(self):
        self.buffer = []
        self.current_track = None
        self.current_chrom = None
        self.file_paths = make_file_names(self.path)
        return self

    def __exit__(self, errtype, value, traceback):
        self.closeCurrentTrack()

    def defineFields(self, fields):
        self.fields = fields

    def newTrack(self, attributes):
        # Close previous track #
        self.closeCurrentTrack()
        # Get a name #
        path = self.file_paths.next()
        # Add it to the result #
        self.tracks.append(path)
        # Create it #
        self.current_track = track.new(path)

    def newFeature(self, feature):
        if feature[0] == self.current_chrom and len(self.buffer) < 1000:
            self.buffer.append(feature[0:])
        else:
            self.flushBuffer()
            self.current_chrom = feature[0]
            self.buffer.append(feature[0:])

    #-----------------------------------------------------------------------------#
    def closeCurrentTrack(self):
        if self.current_track:
            self.flushBuffer()
            self.current_track.save()
            self.current_track.close()
            self.current_track = None
            self.current_chrom = None

    def flushBuffer(self):
        self.current_track.write(self.current_chrom, self.buffer, self.fields)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
