"""
Contains format conversion unittests.
"""

# Built-in modules #
import os

# Internal modules #
import track
from track.common import temporary_path, sqlcmp
from track.test import samples

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class Test_Download(unittest.TestCase):
    def runTest(self):
        url = "http://sugar.epfl.ch/BED/sinclair/genomic/ChIP.bedGraph"
        with track.load(url) as t:
            data = t.read('1', fields=['start','end','attributes'])
            got = list(data)
        expected = []
        self.assertEqual(got, expected)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
