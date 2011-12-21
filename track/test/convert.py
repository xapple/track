"""
Contains format conversion tests.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.test import samples
from track.common import temporary_path, assert_file_equal

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestSQLtoBED(unittest.TestCase):
    """Convert a file to BED"""
    def runTest(self):
        in_path = samples['small_features'][1]['sql']
        out_path = temporary_path('.bed')
        track.convert(in_path, out_path)
        #assert_file_equal(out_path, samples['small_features'][1]['bed'])
        os.remove(out_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
