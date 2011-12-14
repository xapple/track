"""
This module implements the parsing of GFF files.

http://genome.ucsc.edu/FAQ/FAQformat.html#format3

A bug in the python sqlite3 module prevents us form using 'group' for the ninth field.
http://bugs.python.org/issue9750

It is hence replaced with 'attributes'
"""

# Built-in modules #
import shlex

# Internal modules #
from track.parse import Parser
from track.common import iterate_lines
from track.util import strand_to_int

# Constants #
all_fields = ['source', 'name', 'start', 'end', 'score', 'strand', 'frame', 'attributes']

################################################################################
class ParserGFF(Parser):
    format = 'gff'
    def parse(self):
        # Initial variables #
        fields = []
        info   = {}
        # Main loop #
        for number, line in iterate_lines(self.path):
            # Ignored lines #
            if line.startswith("browser "): continue
            # Track headers #
            if line.startswith("track "):
                try:
                    info = dict([p.split('=',1) for p in shlex.split(line[6:])])
                except ValueError:
                    self.handler.error("The track%s seems to have an invalid <track> header line", self.path, number)
                fields = []
                continue
            # Split the lines #
            items = line.split('\t')
            if len(items) == 1: items = line.split()
            # Chromosome #
            chrom = items.pop(0)
            # Length is nine #
            if len(items) != 8:
                self.handler.error("The track%s doesn't have nine columns", self.path, number)
            # Have we started a track already ? #
            if not fields:
                self.handler.newTrack(info, self.name)
                fields = all_fields[0:len(items)]
                self.handler.defineFields(fields)
            # Source field #
            if items[0] == '.': items[0] = ''
            # Name field #
            if items[1] == '.': items[1] = ''
            # Start and end fields #
            try:
                items[2] = int(items[2])
                items[3] = int(items[3])
            except ValueError:
                self.handler.error("The track%s has non integers as interval bounds", self.path, number)
            if items[3] <= items[2]:
                self.handler.error("The track%s has negative or null intervals", self.path, number)
            # Score field #
            if items[4] == '.' or items[4] == '': items[4] = 0.0
            try:
                items[4] = float(items[4])
            except ValueError:
                self.handler.error("The track%s has non floats as score values", self.path, number)
            # Strand field #
            items[5] = strand_to_int(items[5])
            # Frame field #
            if items[6] == '.': items[6] = None
            else:
                try:
                    items[6] = int(items[6])
                except ValueError:
                    self.handler.error("The track%s has non integers as frame value", self.path, number)
            # Group or attribute field #
            if items[7] == '.': items[7] = ''
            # Yield it #
            self.handler.newFeature(chrom, items)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
