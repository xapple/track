"""
This module implements the parsing of bigWig files.

http://genome.ucsc.edu/goldenPath/help/bigWig.html

It requires the binary executable "bigWigToBedGraph" to be installed and listed in the $PATH.
This executable is available here:

http://hgdownload.cse.ucsc.edu/admin/exe/

I started the implementation thinking that I would use the wigToBigWig and bigWigToWig tools provided by UCSC to come and go from the binary format. However, looking more closely at the effects of both programs, it appears that bigWigToWig does not perform as advertised and doesn't create wig files. In reality, the bigWigToWig binary takes bigWig files as input and produces bedGraph files as output. Indeed, the bigWigToWig executable has suspiciously the exact same number of bytes as the bigWigToBedGraph executable...
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.parse import Parser
from track.common import temporary_path, check_executable, run_tool

# Constants #
all_fields = ['start', 'end', 'score']

##mb##############################################################################
class ParserBigWig(Parser):
    def parse(self):
        # Check the binary tools exist #
        check_executable('bigWigToBedGraph')
        # Run the tool #
        bigwig_path   = self.path
        bedgraph_path = temporary_path('.bedGraph')
        run_tool('bigWigToBedGraph', [bigwig_path, bedgraph_path])
        # Now just parse the bedGraph #
        parser = track.parse.get_parser(bedgraph_path)
        parser.name = self.name
        paths = parser(self.handler)
        # Erase the temporary file #
        os.remove(bedgraph_path)
        # Return results #
        return paths

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
