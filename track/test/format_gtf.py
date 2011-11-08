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
        for num, info in sorted(samples['gtf_tracks'].items()):
            # This one is too large #
            if num == 'GenRep': continue
            # Prepare paths #
            orig_gtf_path = info['gtf']
            orig_sql_path = info['sql']
            test_sql_path = temporary_path('.sql')
            # From BED to SQL #
            track.convert(orig_gtf_path, test_sql_path, assembly=12)
            self.assertTrue(assert_file_equal(orig_sql_path, test_sql_path))
            # Clean up #
            os.remove(test_sql_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
