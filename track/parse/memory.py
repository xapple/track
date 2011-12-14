"""
This module implements the parsing of the in-memory data.
In this case, self.path will be a large dictionary.
"""

# Internal modules #
from track.parse import Parser

################################################################################
class ParserMemory(Parser):
    format = 'memory'
    def parse(self):
        self.handler.newTrack({}, self.name)
        for chrom in self.path:
            for feature in self.path[chrom]:
                self.handler.newFeature((chrom,) + feature)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
