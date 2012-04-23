"""
This module implements the parsing of SGA files.

http://ccg.vital-it.ch/chipseq/doc/chipseq_tech.php
"""

# Internal modules #
from track.parse import Parser
from track.util import strand_to_int

# Constants #
all_fields = ['name', 'start', 'end', 'strand', 'score']

################################################################################
class ParserSGA(Parser):
    format = 'sga'

    def parse(self):
        # Initial variables #
        self.handler.newTrack({'int_to_float':'score'}, self.name)
        self.handler.defineFields(all_fields)
        with open(self.path) as f:
            for number, line in enumerate(f):
                items = line.split('\t')
                chrom = items.pop(0)
                if len(items) < 4: self.handler.error("The track%s doesn't have five columns", self.path, number)
                # Name field #
                name = items[0]
                # Start field #
                try: pos = int(items[1])
                except ValueError: self.handler.error("The track%s has non integers as position", self.path, number)
                # Strand field #
                strand = strand_to_int(items[2])
                # Score field #
                try: score = int(items[3])
                except ValueError: self.handler.error("The track%s has non integers as tag count values", self.path, number)
                # Yield it #
                self.handler.newFeature(chrom, (name, pos-1, pos, strand, score))

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
