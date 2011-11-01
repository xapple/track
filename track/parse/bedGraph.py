"""
This module implements the parsing of bedGraph files.

http://genome.ucsc.edu/goldenPath/help/bedgraph.html
"""

# Built-in modules #
import shlex

# Internal modules #
from track.parse import Parser
from track.common import iterate_lines

# Constants #
all_fields = ['start', 'end', 'score']

##mb##############################################################################
class ParserBedGraph(Parser):
    def parse(self):
        # Initial variables #
        declare_track = True
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
                declare_track = True
                continue
            # Split the lines #
            items = line.split('\t')
            if len(items) == 1: items = line.split()
            # Chromosome #
            chrom = items.pop(0)
            # Length is nine #
            if len(items) != 3:
                self.handler.error("The track%s doesn't have four columns", self.path, number)
            # Have we started a track already ? #
            if declare_track:
                declare_track = False
                self.handler.defineFields(all_fields)
                self.handler.newTrack(info, self.name)
            # Start and end fields #
            try:
                items[0] = int(items[0])
                items[1] = int(items[1])
            except ValueError:
                self.handler.error("The track%s has non integers as interval bounds", self.path, number)
            # Score field #
            if items[3] == '.' or items[3] == '': items[3] = 0.0
            try:
                items[3] = float(items[3])
            except ValueError:
                self.handler.error("The track%s has non floats as score values", self.path, number)
            # Yield it #
            self.handler.newFeature(chrom, items)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
