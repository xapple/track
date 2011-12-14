"""
This module implements the sql serialization.
"""

# Built-in modules #
import time

# Internal modules #
import track
from track.serialize import Serializer
from track.common import make_file_names

# Constants #
BUFFER_SIZE = 32767

################################################################################
class SerializerSQL(Serializer):
    format = 'sql'

    def __enter__(self):
        self.buffer = []
        self.fields = None
        self.current_track = None
        self.current_chrom = None
        self.file_paths = make_file_names(self.path)
        return self

    def __exit__(self, errtype, value, traceback):
        if self.current_track: self.closeCurrentTrack()

    def defineFields(self, fields):
        if fields != self.fields: self.flushBuffer()
        self.fields = fields

    def defineChrmeta(self, chrmeta):
        self.current_chrmeta = chrmeta

    def defineAssembly(self, assembly):
        self.current_assembly = assembly

    def newTrack(self, info=None, name=None):
        # Close previous track #
        if self.current_track: self.closeCurrentTrack()
        # Get a file name #
        path = self.file_paths.next()
        # Add it to the result #
        self.tracks.append(path)
        # Create it #
        self.current_track = track.new(path)
        # Add the metadata #
        if info: self.current_track.info.update(info)
        # Add the tags #
        #if name: self.current_track.info['converted_from'] = name
        #self.current_track.info['converted_by'] = 'track package'
        #self.current_track.info['converted_at'] = time.asctime()
        # Benchmark it #
        #self.start_time = time.time()

    def newFeature(self, chrom, feature):
        if chrom == self.current_chrom and len(self.buffer) < BUFFER_SIZE:
            self.buffer.append(feature)
        else:
            self.flushBuffer()
            self.current_chrom = chrom
            self.buffer.append(feature)

    #-----------------------------------------------------------------------------#
    def closeCurrentTrack(self):
        # Empty buffer #
        self.flushBuffer()
        # Add chrmeta #
        if hasattr(self, 'current_chrmeta'): self.current_track.chrmeta = self.current_chrmeta
        # Add assembly #
        if hasattr(self, 'current_assembly'): self.current_track.assembly = self.current_assembly
        # Add the benchmark #
        #self.current_track.info['converted_in'] = time.time() - self.start_time
        # Commit changes #
        self.current_track.save()
        self.current_track.close()
        # Reset varaibles #
        self.current_track = None

    def flushBuffer(self):
        if self.buffer:
            self.current_track.write(self.current_chrom, self.buffer, self.fields)
            self.buffer = []

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
