"""
This module implements the simple parsing of GFF files according to this standard:

http://genome.ucsc.edu/FAQ/FAQformat.html#format3
"""

# Internal modules #
from track.parse.bed import all_fields
from track.simple import SimpleTrack
from track.util import strand_to_int

###########################################################################
class SimpleGFF(SimpleTrack):
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
            # Length is nine #
            if len(items) != 8:
                self.error("The track%s doesn't have nine columns", self.path, number)
            # Source field #
            if items[0] == '.': items[0] = ''
            # Name field #
            if items[1] == '.': items[1] = ''
            # Start and end fields #
            try:
                items[2] = int(items[2])
                items[3] = int(items[3])
            except ValueError:
                self.error("The track%s has non integers as interval bounds", self.path, number)
            if items[3] <= items[2]:
                self.error("The track%s has negative or null intervals", self.path, number)
            # Score field #
            if items[4] == '.' or items[4] == '': items[4] = 0.0
            try:
                items[4] = float(items[4])
            except ValueError:
                self.error("The track%s has non floats as score values", self.path, number)
            # Strand field #
            items[5] = strand_to_int(items[5])
            # Frame field #
            if items[6] == '.': items[6] = None
            else:
                try:
                    items[6] = int(items[6])
                except ValueError:
                    self.error("The track%s has non integers as frame value", self.path, number)
            # Group or attribute field #
            if items[7] == '.': items[7] = ''
            # Yield it #
            yield chrom, items

    #-----------------------------------------------------------------------------#
    @property
    def datatype(self):
        return 'features'

    def guess_fields(self):
        return all_fields

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
