"""
This module implements the parsing of the track object.
"""

# Internal modules #
from track.parse import Parser

################################################################################
class ParserTrack(Parser):
    def parse(self):
        self.handler.defineFields(self.fields)
        self.handler.newTrack(self.attributes)
        for chrom in self.path:
            for feature in self.path.read(chrom):
                self.handler.newFeature(chrom, feature)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
