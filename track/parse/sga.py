"""
This module implements the parsing of SGA files.

http://ccg.vital-it.ch/chipseq/doc/chipseq_tech.php
"""

# Internal modules #
from track.parse import Parser
from track.util import strand_to_int
from track.common import iterate_lines

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

    def parse(self):
        # Initial variables #
        l_chrom, l_name, l_start, l_end, l_strand, l_score = None, None, None, None, None, None
        # Start a new track #
        self.handler.newTrack({'int_to_float':'score'}, self.name)
        self.handler.defineFields(all_fields)
        # Line loop #
        for number, line in iterate_lines(self.path):
            # Ignored lines #
            if line.startswith("browser "): continue
            if line.startswith("track "): continue
            # Split the lines #
            items = line.split('\t')
            if len(items) == 1: items = line.split()
            # Is it a legal line ? #
            if len(items) < 5: self.handler.error("The track%s has less than five columns", self.path, number)
            # Chromosome #
            chrom = items.pop(0)
            # Name field #
            name = items[0]
            # Start and end field #
            try: pos = int(items[1])
            except ValueError: self.handler.error("The track%s has non integers as position", self.path, number)
            start = pos-1
            end = pos
            # Strand field #
            strand = strand_to_int(items[2])
            # Score field #
            try: score = int(items[3])
            except ValueError: self.handler.error("The track%s has non integers as tag count values", self.path, number)
            # Ignore null scores #
            if score == 0: continue
            # Merge adjacent features with same scores #
            if (l_chrom, l_name, l_strand, l_score) == (chrom, name, strand, score) and start == l_end:
                l_end = end
                continue
            else:
                if l_chrom: self.handler.newFeature(l_chrom, (l_name, l_start, l_end, l_strand, l_score))
                l_chrom, l_name, l_start, l_end, l_strand, l_score = chrom, name, start, end, strand, score
        # Last feature #
        if l_chrom: self.handler.newFeature(l_chrom, (l_name, l_start, l_end, l_strand, l_score))

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
