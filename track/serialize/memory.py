"""
This module implements the in-memory serialization.
"""

# Built-in modules #
import collections

# Internal modules #
from track.serialize import Serializer

################################################################################
class SerializerMemory(Serializer):
    def __init__(self):
        self.tracks = []

    def newTrack(self, info=None, name=None):
        self.tracks.append(collections.defaultdict(list))

    def newFeature(self, chrom, feature):
        self.tracks[-1]['chrom'].append(feature)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
