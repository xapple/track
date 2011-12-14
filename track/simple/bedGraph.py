"""
This module implements the simple parsing of bedgraph files according to this standard:

http://genome.ucsc.edu/goldenPath/help/bedgraph.html
"""

# Internal modules #
from track.simple import SimpleTrack

###########################################################################
class SimpleBedgraph(SimpleTrack):
    def read_features(self):
        for number, line in enumerate(self.file):
            # Strip #
            line = line.strip()
            if len(line) == 0: continue
            # Ignored lines #
            if line.startswith("browser "): continue
            if line.startswith("track "):   continue
            if line.startswith("#"):        continue
            # Split the lines #
            items = line.split('\t')
            if len(items) == 1: items = line.split()
            # Chromosome #
            chrom = items.pop(0)
            # Length is three #
            if len(items) != 3:
                self.error("The track%s doesn't have four columns", self.path, number)
            # Start and end fields #
            try:
                items[0] = int(items[0])
                items[1] = int(items[1])
            except ValueError:
                self.error("The track%s has non integers as interval bounds", self.path, number)
            # Score field #
            if items[2] == '.' or items[2] == '': items[2] = 0.0
            try:
                items[2] = float(items[2])
            except ValueError:
                self.error("The track%s has non floats as score values", self.path, number)
            # Yield it #
            yield chrom, items

    def write_features(self, generator):
        for f in generator: yield ' '.join([str(x) for x in f]) + '\n'

    #-----------------------------------------------------------------------------#
    @property
    def datatype(self):
        return 'signal'

    def guess_fields(self):
        return ('start', 'end', 'score')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
