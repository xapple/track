"""
Contains tests for the bigWig format.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.common import temporary_path, assert_file_equal
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
        for num, info in sorted(samples['bigWig_tracks'].items()):
            # Prepare paths #
            orig_bigWig_path = info['bigWig']
            orig_sql_path = info['sql']
            test_sql_path = temporary_path('.sql')
            test_bigWig_path = temporary_path('.bigWig')
            # From bigWig to SQL #
            track.convert(orig_bigWig_path, test_sql_path, assembly='sacCer2')
            self.assertTrue(assert_file_equal(orig_sql_path, test_sql_path))
            # From SQL to bigWig #
            with track.load(test_sql_path) as t: t.roman_to_integer()
            track.convert(test_sql_path, test_bigWig_path)
            self.assertTrue(assert_file_equal(orig_bigWig_path, test_bigWig_path, start_a=1, start_b=1))
            # Clean up #
            os.remove(test_sql_path)
            os.remove(test_bigWig_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
