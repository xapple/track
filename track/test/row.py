"""
Contains tests for the SuperRow object.
"""

# Built-in modules #
import sqlite3

# Internal modules #
from track.pyrow import SuperRow

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestRowSlice(unittest.TestCase):
    def runTest(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = SuperRow
        row = con.execute("select 1, 2, 3, 4").fetchone()
        self.assertTrue(row[0:0]   == (),      "by slice: wrong result for [0:0]")
        self.assertTrue(row[0:1]   == (1,),    "by slice: wrong result for [0:1]")
        self.assertTrue(row[1:3]   == (2,3),   "by slice: wrong result for [1:3]")
        self.assertTrue(row[1:]    == (2,3,4), "by slice: wrong result for [1:]")
        self.assertTrue(row[:3]    == (1,2,3), "by slice: wrong result for [:3]")
        self.assertTrue(row[-2:-1] == (3,),    "by slice: wrong result for [-2:-1]")
        self.assertTrue(row[-2:]   == (3,4),   "by slice: wrong result for [-2:]")

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
