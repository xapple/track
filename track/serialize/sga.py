"""
This module implements the SGA serialization.

http://ccg.vital-it.ch/chipseq/doc/chipseq_tech.php
"""

# Internal modules #
from track.serialize import Serializer

# Constants #
all_fields = ['name', 'start', 'strand', 'score']

################################################################################
class SerializerSGA(Serializer):
    format = 'sga'

    def __enter__(self):
        self.file = open(self.path, 'w')
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        raise NotImplementedError("SGA creation hasn't been coded yet.")

    def newTrack(self, info=None, name=None):
        raise NotImplementedError("SGA creation hasn't been coded yet.")

    def newFeature(self, chrom, feature):
        raise NotImplementedError("SGA creation hasn't been coded yet.")

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
