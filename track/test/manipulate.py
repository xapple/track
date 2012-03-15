"""
Run all the manips unittest by creating a test suite.

To run this in ipython type::

    [1] from track.manipulate import tests, list_of_manip_names
    [2] t = tests.TestManips()
    [3] for name in list_of_manip_names: print name, getattr(t,name)()
"""

# Built-in modules #
import os

# Internal modules #
import track
from track import manipulate
from track.manipulate import window_smoothing, mean_score_by_feature
from track.manipulate import complement, merge_scores, threshold
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
class TestManips(unittest.TestCase):
    def runTest():pass

def make_fn(manip_name):
    def test_fn(self):
        self.maxDiff = None
        manip = getattr(manipulate, manip_name)
        for got, expected in manip.test(): self.assertEqual(got, expected)
    return test_fn

for name in manipulate.list_of_manip_names:
    setattr(TestManips, name, make_fn(name))
suite = unittest.TestLoader().loadTestsFromTestCase(TestManips)

###################################################################################
class TestComplement(unittest.TestCase):
    """Test a complement call via tracks."""
    def runTest(self):
        in_path = samples['small_features'][1]['sql']
        out_path = temporary_path('.bed')
        with track.load(in_path) as t:
            result = complement(t)
            result.export(out_path)
        with track.load(out_path) as t:
            data = t.read('chrI')
            got = map(tuple, data)
        expected = [( 10,     20),
                    ( 30,     40),
                    ( 50,     60),
                    ( 80,     90),
                    (110,    120),
                    (135, 230208)]
        self.assertEqual(got, expected)
        os.remove(out_path)

class TestWindowSmooth(unittest.TestCase):
    """Test a window_smoothing call via tracks."""
    def runTest(self):
        in_path = temporary_path('.sql')
        out_path = temporary_path('.sql')
        with track.new(in_path) as t:
            t.fields = ('start','end','score')
            t.assembly = 'sacCer2'
            t.write('chrI',[(0,2,10),(2,4,20),(6,8,10)])
            result = window_smoothing(t, 2)
            result.export(out_path)
        with track.load(out_path) as t:
            data = t.read('chrI')
            got = map(tuple, data)
        expected = [(0,  1,   8.0),
                    (1,  3,  12.0),
                    (3,  5,  10.0),
                    (5,  6,   8.0),
                    (6,  9,   4.0),
                    (9,  10,  2.0)]
        self.assertEqual(got, expected)
        os.remove(in_path)
        os.remove(out_path)

###################################################################################
class TestMergeScores(unittest.TestCase):
    """Test a merge scores call via files."""
    def runTest(self):
        in_paths = [samples['small_signals'][1]['sql'],
                    samples['small_signals'][2]['sql'],
                    samples['small_signals'][3]['sql']]
        out_path = temporary_path('.sql')
        t = merge_scores(in_paths)
        t.export(out_path)
        with track.load(out_path) as t:
            data = t.read('chrI')
            got = map(tuple, data)
        expected = [( 0,    5,    2.0 + 0.6666666666666666),
                    ( 5,   10,    4.0),
                    ( 20,  30,   10.0),
                    ( 30,  40,   30.0),
                    ( 40,  50,   26.0 + 0.666666666666666),
                    ( 50,  60,  120.0),
                    ( 60,  68,  100.0),
                    ( 68,  70,  200.0),
                    ( 70,  80,  100.0),
                    ( 90, 110,    3.0),
                    (120, 130,   10.0)]
        self.assertEqual(got, expected)
        os.remove(out_path)

class TestMeanScores(unittest.TestCase):
    """Test a mean score by feature call via files."""
    def runTest(self):
        x_path = samples['small_signals'][4]['sql']
        y_path = samples['small_features'][4]['sql']
        out_path = temporary_path('.sql')
        t = mean_score_by_feature(x_path,y_path)
        t.export(out_path)
        with track.load(out_path) as t:
            data = t.read('chrI')
            got = map(tuple, data)
        expected = [(10, 20, 15.0, u'Lorem', 1),
                    (30, 40, 50.0, u'Ipsum', 1)]
        self.assertEqual(got, expected)
        os.remove(out_path)

class TestThreshold(unittest.TestCase):
    """Test a threshold call via files."""
    def runTest(self):
        in_path = samples['small_signals'][4]['sql']
        out_path = temporary_path('.sql')
        t = threshold(in_path, 8000.0)
        t.export(out_path)
        with track.load(out_path) as t:
            data = t.read('chrI')
            got = map(tuple, data)
        expected = [(120, 122, 9000.0)]
        self.assertEqual(got, expected)
        os.remove(out_path)
