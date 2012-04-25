"""
Contains tests for the SGA format.
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
class TestImport(unittest.TestCase):
    def runTest(self):
        for num, info in sorted(samples['sga_tracks'].items()):
            # Prepare paths #
            orig_sga_path = info['sga']
            orig_sql_path = info['sql']
            test_sql_path = temporary_path('.sql')
            # From SGA to SQL #
            track.convert(orig_sga_path, test_sql_path, assembly='hg19')
            self.assertTrue(assert_file_equal(orig_sql_path, test_sql_path))
            # Clean up #
            os.remove(test_sql_path)

class TestExport(unittest.TestCase):
    def runTest(self):
        info = samples['small_signals'][1]
        # Prepare paths #
        orig_sql_path = info['sql']
        orig_sga_path = info['sga']
        test_sga_path = temporary_path('.sga')
        # From SGA to SQL #
        track.convert(orig_sql_path, test_sga_path, assembly='hg19')
        self.assertTrue(assert_file_equal(orig_sga_path, test_sga_path))
        # Clean up #
        os.remove(test_sga_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
