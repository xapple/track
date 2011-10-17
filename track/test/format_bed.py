"""
Contains tests for the BED format.
We will do a roundtrips for several sample validation tracks.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.common import temporary_path, assert_sql_equal
from track.test import bed_samples

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestBED(unittest.TestCase):
    def runTest(self):
        for info in bed_samples:
            orig_bed_path = info['bed']
            orig_sql_path = info['sql']
            test_sql_path = temporary_path('.sql')
            test_bed_path = temporary_path('.bed')
            # From BED to SQL #
            track.convert(orig_bed_path, test_sql_path)
            with track.load(test_sql_path) as t: t.assembly = 'sacCer2'
            self.assertTrue(assert_sql_equal(orig_sql_path, test_sql_path))
            # From SQL to BED #
            track.convert(test_sql_path, test_bed_path)
            with open(orig_bed_path, 'r') as f: A = f.read().split('\n')
            with open(test_bed_path, 'r') as f: B = f.read().split('\n')
            self.assertEqual(A[1:], B)
            # Clean up #
            os.remove(test_sql_path)
            os.remove(test_bed_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
