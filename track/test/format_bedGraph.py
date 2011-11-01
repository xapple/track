"""
Contains tests for the bedGraph format.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.common import temporary_path, assert_sql_equal, assert_file_equal
from track.test import samples

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestRoundtrip(unittest.TestCase):
    def runTest(self):
        for num, info in sorted(samples['bedGraph_tracks'].items()):
            # Prepare paths #
            orig_bedGraph_path = info['bedGraph']
            orig_sql_path = info['sql']
            test_sql_path = temporary_path('.sql')
            test_bedGraph_path = temporary_path('.bedGraph')
            # From GFF to SQL #
            track.convert(orig_bedGraph_path, test_sql_path)
            with track.load(test_sql_path) as t: t.assembly = 'sacCer2'
            self.assertTrue(assert_sql_equal(orig_sql_path, test_sql_path))
            # From SQL to GFF #
            with track.load(test_sql_path) as t: [t.rename(chrom, 'chr'+chrom) for chrom in t]
            track.convert(test_sql_path, test_bedGraph_path)
            self.assertTrue(assert_file_equal(orig_bedGraph_path, test_bedGraph_path, start_a=1, start_b=1))
            # Clean up #
            os.remove(test_sql_path)
            os.remove(test_bedGraph_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
