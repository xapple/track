"""
Contains tests for the 'simple' submodule that parses files and
returns only generators.
"""

# Internal modules #
from track.simple import load
from track.test import samples

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
        in_path = samples['small_features'][4]['bed']
        with load(in_path) as t:
            got = []
            for chrom, data in t:
                for feature in data:
                    got.append(tuple([chrom] + feature))
        expected = [('chr1', 10, 20, 'Lorem', 1.0, 1),
                    ('chr1', 30, 40, 'Ipsum', 2.0, 1),
                    ('chr2', 10, 20, 'Dolor', 3.0, 1)]
        self.assertEqual(got, expected)

###################################################################################
class TestWIG(unittest.TestCase):
    def runTest(self):
        in_path = samples['small_signals'][3]['wig']
        with load(in_path) as t:
            got = []
            for chrom, data in t:
                for feature in data:
                    got.append(tuple([chrom] + feature))
        expected = [('chr1', 20, 50, 20.0),
                    ('chr1', 50, 80, 300.0)]
        self.assertEqual(got, expected)

###################################################################################
class TestBedGraph(unittest.TestCase):
    def runTest(self):
        in_path = samples['bedGraph_tracks'][5]['bedGraph']
        with load(in_path) as t:
            got = []
            for chrom, data in t:
                for feature in data:
                    got.append(tuple([chrom] + feature))
        expected = [('chr1',  0, 10, -1.0),
                    ('chr1', 20, 30, -1.75),
                    ('chr1', 40, 50, -2.5)]
        self.assertEqual(got, expected)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
