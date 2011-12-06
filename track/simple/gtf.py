"""
This module implements the simple parsing of GTF files according to this standard:

http://genome.ucsc.edu/FAQ/FAQformat.html#format4
"""

# Built-in modules #
import shlex

# Internal modules #
from track.parse.bed import all_fields
from track.simple import SimpleTrack
from track.util import strand_to_int

###########################################################################
class SimpleGTF(SimpleTrack):
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
            if len(items) > 8: items = items[0:8] + [' '.join(items[8:])]
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
            # The last special column #
            attr = shlex.split(items.pop())
            attr = dict([(attr[i],attr[i+1].strip(';')) for i in xrange(0,len(attr),2)])
            items += attr.values()
            # Yield it #
            yield chrom, items

    def write_features(self, generator):
        for f in generator: yield ' '.join([str(x) for x in f]) + '\n'

    #-----------------------------------------------------------------------------#
    @property
    def datatype(self):
        return 'features'

    def guess_fields(self):
        for line in self.file:
            line = line.strip()
            if len(line) == 0:              continue
            if line.startswith("#"):        continue
            if line.startswith("track "):   continue
            if line.startswith("browser "): continue
            # Split the line #
            items = line.split('\t')
            if len(items) == 1: items = line.split()
            if len(items) > 8: items = items[0:8] + [' '.join(items[8:])]
            # Check the length #
            if len(items) != 9:
                self.error("The track%s doesn't have nine columns", self.path)
            # Get the result #
            attr = shlex.split(items.pop())
            attr = dict([(attr[i],attr[i+1].strip(';')) for i in xrange(0,len(attr),2)])
            result = all_fields + attr.keys()
        self.file.seek(0)
        return result

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
