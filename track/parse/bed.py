"""
This module implements the parsing of BED files according to this standard:

http://genome.ucsc.edu/FAQ/FAQformat.html#format3
"""

# Built-in modules #
import shlex

# Internal modules #
from track.parse import Parser
from track.common import iterate_lines
from track.util import strand_to_int

# Constants #
all_fields = ['start', 'end', 'name', 'score', 'strand', 'thick_start',
              'thick_end', 'item_rgb', 'block_count', 'block_sizes', 'block_starts']

################################################################################
class ParserBED(Parser):
    format = 'bed'
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
            # Have we started a track already ? #
            if not fields:
                self.handler.newTrack(info, self.name)
                fields = all_fields[0:len(items)]
                self.handler.defineFields(fields)
            # Start and end fields #
            try:
                items[0] = int(items[0])
                items[1] = int(items[1])
            except ValueError:
                self.handler.error("The track%s has non integers as interval bounds", self.path, number)
            except IndexError:
                self.handler.error("The track%s has less than two columns", self.path, number)
            # All following fields are optional #
            try:
                # Name field #
                if items[2] == '.': items[2] = ''
                # Score field #
                if items[3] == '.' or items[3] == '': items[3] = 0.0
                try:
                    items[3] = float(items[3])
                except ValueError:
                    self.handler.error("The track%s has non floats as score values", self.path, number)
                # Strand field #
                items[4] = strand_to_int(items[4])
                # Thick starts #
                try:
                    items[5] = float(items[5])
                except ValueError:
                    self.handler.error("The track%s has non integers as thick starts", self.path, number)
                # Thick ends #
                try:
                    items[6] = float(items[6])
                except ValueError:
                    self.handler.error("The track%s has non integers as thick ends", self.path, number)
                # Too many fields #
                if len(items) > 11:
                    self.handler.error("The track%s has more than twelve columns", self.path, number)
            # All index errors are ignored since the fields above three are optional #
            except IndexError:
                pass
            finally:
                self.handler.newFeature(chrom, items)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
