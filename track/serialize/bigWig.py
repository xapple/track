"""
This module implements the bigWig serialization.

It requires the binary executable "bedGraphToBigWig" to be installed and listed in the $PATH.
This executable is available here:

http://hgdownload.cse.ucsc.edu/admin/exe/
"""

# Internal modules #
from track.serialize.bedGraph import SerializerBedGraph
from track.common import temporary_path, check_executable, run_tool
from track.util import serialize_chr_file

# Constants #
all_fields = ['start', 'end', 'score']

################################################################################
class SerializerBigWig(SerializerBedGraph):
    def __enter__(self):
        # First just serialize it as a bedGrap #
        bedgraph_path = temporary_path('.bedGraph')
        self.file = open(bedgraph_path, 'w')
        return self

    def __exit__(self, errtype, value, traceback):
        # The three paths #
        bigwig_path   = self.path
        bedgraph_path = self.file.name
        chrfile_path  = temporary_path('.chr')
        # Close the bedGraph #
        self.file.close()
        # Check the binary tools exist #
        check_executable('bedGraphToBigWig')
        # Make the chr file #
        serialize_chr_file(self.chrmeta, chrfile_path)
        # Run the tool #
        run_tool('bedGraphToBigWig', [bedgraph_path, chrfile_path, bigwig_path])

    def defineChrmeta(self, chrmeta):
        self.chrmeta = chrmeta

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
