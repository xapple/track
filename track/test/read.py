"""
Contains format conversion unittests.
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
class Test_Read(unittest.TestCase):
    def runTest(self):
        self.skipTest('')
        in_path = samples['features'][1]['sql']
        with track.load(in_path) as t:
            data = t.read('chr1', fields=['start','end','attributes'])
            got = list(data)
        expected = []
        self.assertEqual(got, expected)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
