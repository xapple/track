"""
Contains the compressed file tests.
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
        # Prepare paths #
        orig_gzip_path = samples['gzip_tracks'][1]['gzip']
        orig_sql_path  = samples['small_features'][1]['sql']
        test_sql_path  = temporary_path('.sql')
        # From BED to SQL #
        track.convert(orig_gzip_path, test_sql_path, assembly='sacCer2')
        self.assertTrue(assert_file_equal(orig_sql_path, test_sql_path))
        # Clean up #
        os.remove(test_sql_path)

class TestWithoutExtension(unittest.TestCase):
    def runTest(self):
        in_path = samples['gzip_tracks'][4]['gzip']
        with track.load(in_path) as t:
            data = t.read()
            got = list(data)
        expected = [('chr1', 10, 20, u'Lorem', 1.0, 1),
                    ('chr1', 30, 40, u'Ipsum', 2.0, 1),
                    ('chr2', 10, 20, u'Dolor', 3.0, 1)]
        self.assertEqual(got, expected)
