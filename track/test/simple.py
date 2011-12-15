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
        in_path = samples['small_signals'][5]['bedgraph']
        with load(in_path) as t:
            got = []
            for chrom, data in t:
                for feature in data:
                    got.append(tuple([chrom] + feature))
        expected = [('chr1',  0, 10, -1.0),
                    ('chr1', 20, 30, -1.75),
                    ('chr1', 40, 50, -2.5)]
        self.assertEqual(got, expected)

###################################################################################
class TestGFF(unittest.TestCase):
    def runTest(self):
        in_path = samples['gff_tracks'][1]['gff']
        with load(in_path) as t:
            got = []
            for chrom, data in t:
                for feature in data:
                    got.append(tuple([chrom] + feature))
        expected = [('chr1', 'TeleGene', 'enhancer', 1000000, 1001000, 500.0,  1, None, 'touch1'),
                    ('chr1', 'TeleGene', 'promoter', 1010000, 1010100, 900.0,  1, None, 'touch1'),
                    ('chr1', 'TeleGene', 'promoter', 1020000, 1020010, 800.0, -1, None, 'touch2')]
        self.assertEqual(got, expected)

###################################################################################
class TestGTF(unittest.TestCase):
    def runTest(self):
        in_path = samples['gtf_tracks'][1]['gtf']
        with load(in_path) as t:
            got = []
            for chrom, data in t:
                for feature in data:
                    got.append(tuple([chrom] + feature))
        expected = [('chr1', 'Twinscan', 'CDS', 380, 401, 0.0, 1, 0, '001.1', '001'),
                    ('chr1', 'Twinscan', 'CDS', 501, 650, 0.0, 1, 2, '001.1', '001'),
                    ('chr1', 'Twinscan', 'CDS', 700, 707, 0.0, 1, 2, '001.1', '001'),
                    ('chr1', 'Twinscan', 'start_codon', 380, 382, 0.0, 1, 0, '001.1', '001'),
                    ('chr1', 'Twinscan', 'stop_codon', 708, 710, 0.0, 1, 0, '001.1', '001')]
        self.assertEqual(got, expected)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
