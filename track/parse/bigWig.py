"""
This module implements the parsing of bigWig files.

http://genome.ucsc.edu/goldenPath/help/bigWig.html
"""

# Built-in modules #
import shlex

# Internal modules #
from track.parse import Parser
from track.common import iterate_lines

# Constants #
all_fields = ['start', 'end', 'score']

##mb##############################################################################
class ParserBigWig(Parser):
    def parse(self):
        proc = subprocess.Popen(['bedGraphToBigWig', bedgraph_path, yeast_chr_file, d['path']], stderr = subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if stderr: raise Exception("The tool bedGraphToBigWig exited with message: " + '"' + stderr.strip('\n') + '"')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
