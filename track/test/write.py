"""
Contains chained write tests.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.test import samples
from track.common import temporary_path, assert_file_equal

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestChain(unittest.TestCase):
    def runTest(self):
        in_path = samples['small_signals'][7]['sql']
        out_path = temporary_path('.sql')
        with track.load(in_path) as i:
            with track.new(out_path) as o:
                for chrom in i:
                    if i.count(chrom) != 0: o.write(chrom, i.read(chrom))
                o.assembly = i.assembly
                o.info = i.info
        self.assertTrue(assert_file_equal(in_path, out_path, end=9))
        os.remove(out_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
