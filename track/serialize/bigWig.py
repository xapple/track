"""
This module implements the bigWig serialization.


It requires the binary executable "bedGraphToBigWig" to be installed and listed in the $PATH.
This executable is available here:

http://hgdownload.cse.ucsc.edu/admin/exe/
"""

# Internal modules #
from track.serialize import Serializer
from track.common import check_executable, run_tool

# Constants #
all_fields = ['start', 'end', 'score']

################################################################################
class SerializerBigWig(Serializer):
    def __enter__(self):
        # Check the binary tools exist #
        check_executable('bedGraphToBigWig')
        # Make the chr file #
        chrfile = self.chrmeta.write_file(sep=' ')
        self.run_tool('bedGraphToBigWig', [source, chrfile, dest])

        # Return self #
        return self

    def defineFields(self, fields):
        pass

    def newTrack(self, info=None, name=None):
        pass

    def newFeature(self, chrom, feature):
        pass

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
