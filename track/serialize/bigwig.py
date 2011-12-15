"""
This module implements the bigwig serialization.

It requires the binary executable "bedGraphToBigWig" to be installed and listed in the $PATH.
This executable is available here:

http://hgdownload.cse.ucsc.edu/admin/exe/
"""

# Built-in modules #
import os

# Internal modules #
from track.serialize.bedgraph import SerializerBedgraph
from track.common import temporary_path, check_executable, run_tool
from track.util import serialize_chr_file

# Constants #
all_fields = ['start', 'end', 'score']

################################################################################
class SerializerBigwig(SerializerBedgraph):
    def __enter__(self):
        # Just serialize it as a bedgraph first #
        self.tmp_path = temporary_path('.bedgraph')
        self.file = open(self.tmp_path, 'w')
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()
        bedgraph_to_bigwig(self.tmp_path, self.chrmeta, self.path)
        self.tracks = [self.path]
        os.remove(self.tmp_path)

################################################################################
def bedgraph_to_bigwig(bedgraph_path, chrmeta, bigwig_path):
    """
    Converts a bedgraph file to a bigwig file.

    :param bedgraph_path: The path to the bedgraph file to read.
    :type  bedgraph_path: string
    :param chrmeta: The chromosome metadata.
    :type  chrmeta: dict
    :param bigwig_path: The path to the bedbig file to create.
    :type  bigwig_path: string
    :returns: None
    """
    # Check the binary tool exists #
    check_executable('bedGraphToBigWig')
    # Make the chr file #
    chrfile_path = temporary_path('.chr')
    serialize_chr_file(chrmeta, chrfile_path)
    # Run the tool #
    run_tool('bedGraphToBigWig', [bedgraph_path, chrfile_path, bigwig_path])
    # Remove the chr file #
    os.remove(chrfile_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
