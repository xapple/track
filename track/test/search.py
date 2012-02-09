"""
Contains tests for the track.search method.
"""

# Internal modules #
import track
from track.test import samples

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestTwoParameters(unittest.TestCase):
    """A simple case with two fields"""
    def runTest(self):
        in_path = samples['small_features'][1]['sql']
        with track.load(in_path) as t:
            data = t.search({'start':'2','name':'feature'})
            got = list([tuple(x) for x in data])
        expected = [(u'chrI', 2, 8, u'Validation feature 2', 0.0),
                    (u'chrI', 20, 30, u'Validation feature 3', 10.0),
                    (u'chrI', 25, 30, u'Validation feature 4', 0.0),
                    (u'chrI', 120, 130, u'Validation feature 11', 10.0),
                    (u'chrI', 125, 135, u'Validation feature 12', 5.0)]
        self.assertEqual(got, expected)

class TestNoResults(unittest.TestCase):
    """A case with no results"""
    def runTest(self):
        in_path = samples['small_features'][1]['sql']
        with track.load(in_path) as t:
            data = t.search({'start':'2','name':'feature'}, exact_match=True)
            got = list(data)
        expected = []
        self.assertEqual(got, expected)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
