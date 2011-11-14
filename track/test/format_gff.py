"""
Contains tests for the BED format.
We will do a roundtrips for several sample validation tracks.
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
        for num, info in sorted(samples['gff_tracks'].items()):
            # Prepare paths #
            orig_gff_path = info['gff']
            orig_sql_path = info['sql']
            test_sql_path = temporary_path('.sql')
            test_gff_path = temporary_path('.gff')
            # From GFF to SQL #
            track.convert(orig_gff_path, test_sql_path, assembly='sacCer2')
            self.assertTrue(assert_file_equal(orig_sql_path, test_sql_path))
            # From SQL to GFF #
            with track.load(test_sql_path) as t: t.roman_to_integer()
            track.convert(test_sql_path, test_gff_path)
            self.assertTrue(assert_file_equal(orig_gff_path, test_gff_path, start_a=1, start_b=1))
            # Clean up #
            os.remove(test_sql_path)
            os.remove(test_gff_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
