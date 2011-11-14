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
class TestConversion(unittest.TestCase):
    def runTest(self):
        for num, info in sorted(samples['yeast_features'].items()):
            # Prepare paths #
            orig_bed_path = info['bed']
            orig_sql_path = info['sql']
            test_sql_path = temporary_path('.sql')
            # From BED to SQL #
            track.convert(orig_bed_path, test_sql_path, assembly='sacCer2')
            self.assertTrue(assert_file_equal(orig_sql_path, test_sql_path))
            # Clean up #
            os.remove(test_sql_path)

class TestRoundtrip(unittest.TestCase):
    def runTest(self):
        for num, info in sorted(samples['small_features'].items()):
            # Prepare paths #
            orig_bed_path = info['bed']
            orig_sql_path = info['sql']
            test_sql_path = temporary_path('.sql')
            test_bed_path = temporary_path('.bed')
            # From BED to SQL #
            track.convert(orig_bed_path, test_sql_path, assembly='sacCer2')
            self.assertTrue(assert_file_equal(orig_sql_path, test_sql_path))
            # From SQL to BED #
            with track.load(test_sql_path) as t: t.roman_to_integer()
            track.convert(test_sql_path, test_bed_path)
            self.assertTrue(assert_file_equal(orig_bed_path, test_bed_path, start_b=1))
            # Clean up #
            os.remove(test_sql_path)
            os.remove(test_bed_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
