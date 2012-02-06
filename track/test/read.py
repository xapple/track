"""
Contains simple reading tests.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.common import temporary_path
from track.test import samples

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestWithChrom(unittest.TestCase):
    """Read all features from a track"""
    def runTest(self):
        in_path = samples['small_features'][1]['sql']
        with track.load(in_path) as t:
            data = t.read()
            got = list(data)
        expected = [('chrI', 0, 10, u'Validation feature 1', 10.0),
                    ('chrI', 2, 8, u'Validation feature 2', 0.0),
                    ('chrI', 20, 30, u'Validation feature 3', 10.0),
                    ('chrI', 25, 30, u'Validation feature 4', 0.0),
                    ('chrI', 40, 45, u'Validation feature 5', 0.0),
                    ('chrI', 40, 50, u'Validation feature 6', 10.0),
                    ('chrI', 60, 70, u'Validation feature 7', 10.0),
                    ('chrI', 70, 80, u'Validation feature 8', 10.0),
                    ('chrI', 90, 100, u'Validation feature 9', 10.0),
                    ('chrI', 90, 110, u'Validation feature 10', 10.0),
                    ('chrI', 120, 130, u'Validation feature 11', 10.0),
                    ('chrI', 125, 135, u'Validation feature 12', 5.0)]
        self.assertEqual(got, expected)

class TestWithoutName(unittest.TestCase):
    """Read some features from a track"""
    def runTest(self):
        in_path = samples['small_features'][5]['sql']
        with track.load(in_path) as t:
            data = t.read('chrI', ('start', 'end', 'name', 'score'))
            got = tuple(data.next())
        expected = (14, 19, u'', 0.0)
        self.assertEqual(got, expected)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
