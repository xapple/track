"""
This module implements the SGA serialization.

http://ccg.vital-it.ch/chipseq/doc/chipseq_tech.php
"""

# Internal modules #
from track.serialize import Serializer
from track.util import int_to_strand

# Constants #
all_fields = ['start', 'end', 'name', 'strand', 'score']
defaults   = [None, None, 'signal', '0', '0']

################################################################################
class SerializerSGA(Serializer):
    format = 'sga'

    def __enter__(self):
        self.file = open(self.path, 'w')
        self.indices = []
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        # Check for required fields #
        if 'start' not in fields or 'end' not in fields:
            self.error("You tried to write an SGA file without a start and end field")
        # Check that all fields are legal #
        for f in fields:
            if f not in all_fields:
                message = "You tried to write a '%s' field to a SGA file. Possible fields are: %s"
                self.error(message % (f, all_fields))
        # Find indicies #
        for i,f in enumerate(all_fields):
            if f in fields: self.indices.append(fields.index(f))
            else: self.indices.append(defaults[i])

    def newTrack(self, info=None, name=None):
        if not info: info = {}
        info['type'] = 'sga'
        info['converted_by'] = __package__
        self.tracks.append(self.path)

    def newFeature(self, chrom, feature):
        # Put the fields in the right order #
        feature = [feature[i] if isinstance(i,int) else i for i in self.indices]
        start, end, name, strand, score = feature
        # Convert the score #
        try: score = str(int(score))
        except ValueError: pass
        # Convert the strand #
        try: strand = int_to_strand(strand)
        except ValueError: pass
        # Write one line #
        for i in range(end-start):
            self.file.write('\t'.join((chrom, name, str(start+1+i), strand, score)) + '\n')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
