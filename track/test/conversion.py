"""
Contains format conversion unittests.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.test import collection

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
        d = track_collections['Validation'][1]
        with track.load(d['path_sql']) as t:
            # Just the first feature #
            data = t.read()
            self.assertEqual(data.next(), ('chr1', 0, 10, 'Validation feature 1', 10.0, 0))
            # Number of features #
            data = t.read()
            self.assertEqual(len(list(data)), 12)
            # Different fields #
            data = t.read('chr1', fields=['score'])
            expected = [(10.0,), (0.0,), (10.0,), (0.0,), (0.0,), (10.0,), (10.0,), (10.0,), (10.0,), (10.0,), (10.0,), (5.0,)]
            self.assertEqual(list(data), expected)
            # Empty result #
            data = t.read({'chr':'chr2','start':0,'end':10})
            self.assertEqual(list(data), [])

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
