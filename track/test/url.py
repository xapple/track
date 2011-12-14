"""
Contains URL download tests.
"""

# Internal modules #
import track

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestDownload(unittest.TestCase):
    def runTest(self):
        url = "http://salt.epfl.ch/BED/sinclair/genomic/ChIP.bedGraph"
        with track.load(url) as t:
            got = t.count('chrY')
            expected = 577
        self.assertEqual(got, expected)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
