"""
This module implements the simple parsing of BED files according to this standard:

http://genome.ucsc.edu/FAQ/FAQformat.html#format3
"""

# Internal modules #
from track.parse.bed import all_fields
from track.simple import SimpleTrack
from track.util import strand_to_int, int_to_strand

################################################################################
class SimpleBED(SimpleTrack):
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
            # Start and end fields #
            try:
                items[0] = int(items[0])
                items[1] = int(items[1])
            except ValueError:
                self.error("The track%s has non integers as interval bounds", self.path, number)
            except IndexError:
                self.error("The track%s has less than two columns", self.path, number)
            # All following fields are optional #
            try:
                # Name field #
                if items[2] == '.': items[2] = ''
                # Score field #
                if items[3] == '.' or items[3] == '': items[3] = 0.0
                try:
                    items[3] = float(items[3])
                except ValueError:
                    self.error("The track%s has non floats as score values", self.path, number)
                # Strand field #
                items[4] = strand_to_int(items[4])
                # Thick starts #
                try:
                    items[5] = float(items[5])
                except ValueError:
                    self.error("The track%s has non integers as thick starts", self.path, number)
                # Thick ends #
                try:
                    items[6] = float(items[6])
                except ValueError:
                    self.error("The track%s has non integers as thick ends", self.path, number)
            # All index errors are ignored since the fields above three are optional #
            except IndexError:
                pass
            finally:
                yield chrom, items

    def write_features(self, generator):
        fields = ['start', 'end']
        for f in all_fields[2:]:
            if f in self.fields: fields.append(f)
            else: break
        for feature in generator:
            f = list(feature)
            try:
                f[5] = int_to_strand(feature[5])
            except IndexError:
                pass
            yield '\t'.join([str(x) for x in f]) + '\n'

    #-----------------------------------------------------------------------------#
    @property
    def datatype(self):
        return 'features'

    def guess_fields(self):
        for line in self.file:
            line = line.strip("\n").lstrip()
            if len(line) == 0:              continue
            if line.startswith("#"):        continue
            if line.startswith("track "):   continue
            if line.startswith("browser "): continue
            line = line.split('\t')
            if len(line) == 1: line = line.split()
            self.num_fields = len(line) - 1
            if self.num_fields < 2:
                raise Exception("The file '" + self._path + "' has less than three columns and is hence not a valid BED file.")
            if self.num_fields > len(all_fields):
                raise Exception("The file '" + self._path + "' has too many columns and is hence not a valid BED file.")
            result = all_fields[0:max(5,self.num_fields)]
        self.file.seek(0)
        return result

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
