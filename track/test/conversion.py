"""
Contains format conversion unittests.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.common import temporary_path, assert_sql_equal
from track.test import samples

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class Test_BED_to_SQL(unittest.TestCase):
    def runTest(self):
        in_path       = samples['features'][1]['bed']
        expected_path = samples['features'][1]['sql']
        out_path = temporary_path('.sql')
        track.convert(in_path, out_path)
        with track.load(out_path) as t: t.assembly = 'sacCer2'
        self.assertTrue(assert_sql_equal(expected_path, out_path))
        os.remove(out_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
