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
class TestVector(unittest.TestCase):
    """A simple case without boundaries"""
    def runTest(self):
        in_path = samples['small_features'][4]['sql']
        with track.load(in_path) as t:
            data = t.get_full_score_vector('chrI')
            got = list(data)
        expected = [0.0]*10 + [1.0]*10 + [0.0]*10 + [2.0]*10 + [0.0]*230168
        self.assertEqual(got, expected)

###################################################################################
class TestNoEnd(unittest.TestCase):
    """A simple case on a track without specifying an end"""
    def runTest(self):
        in_path = samples['small_features'][4]['sql']
        with track.load(in_path, readonly=True) as t:
            t.chrmeta = {}
            data = t.get_full_score_vector('chrI')
            got = list(data)
        expected = [0.0]*10 + [1.0]*10 + [0.0]*10 + [2.0]*10
        self.assertEqual(got, expected)

###################################################################################
class TestBoundaries(unittest.TestCase):
    """A simple case with boundaries"""
    def runTest(self):
        in_path = samples['small_features'][4]['sql']
        with track.load(in_path) as t:
            data = t.get_partial_score_vector('chrI', 15, 35)
            got = list(data)
        expected = [1.0]*5 + [0.0]*10 + [2.0]*5
        self.assertEqual(got, expected)

###################################################################################
class TestNoScore(unittest.TestCase):
    """A simple case on a track without scores"""
    def runTest(self):
        in_path = samples['small_features'][5]['sql']
        with track.load(in_path) as t:
            data = t.get_partial_score_vector('chrI', 10, 30)
            got = list(data)
        expected = [0.0]*4 + [1.0]*5 + [0.0]*8 + [1.0]*3
        self.assertEqual(got, expected)

###################################################################################
class TestOverlaps(unittest.TestCase):
    """A case on a feature track that has internal overlaps"""
    def runTest(self):
        in_path = samples['small_features'][1]['sql']
        with track.load(in_path) as t:
            data = t.get_partial_score_vector('chrI', 0, 50)
            got = list(data)
        expected = [10.0]*10 + [0.0]*10 + [10.0]*10 + [0.0]*15 + [10.0]*5
        self.assertEqual(got, expected)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
