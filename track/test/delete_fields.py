"""
Contains tests for ``t.delete_fields()``.
"""

# Built-in modules #
import os, shutil

# Internal modules #
import track
from track.test import samples
from track.common import temporary_path

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class Test(unittest.TestCase):
    def runTest(self):
        orig_path = samples['small_features'][2]['sql']
        test_path = temporary_path('.sql')
        shutil.copy(orig_path, test_path)
        with track.load(test_path) as t:
            t.delete_fields(['name','strand'])
            got = list(t.read())
        expected = [('chrI',  10,  20, 0.1),
                    ('chrI',  30,  40, 0.2),
                    ('chrI',  50,  60, 0.1),
                    ('chrI',  70,  80, 0.2),
                    ('chrI',  90, 100, 0.0),
                    ('chrI', 110, 120, 0.4),
                    ('chrI', 130, 150, 0.4),
                    ('chrI', 180, 190, 0.1),
                    ('chrI', 180, 200, 0.1),
                    ('chrI', 210, 220, 0.2),
                    ('chrI', 230, 240, 0.1),
                    ('chrI', 250, 260, 0.2),
                    ('chrI', 270, 280, 0.0),
                    ('chrI', 290, 300, 0.7)]
        self.assertEqual(got, expected)
        # Clean up #
        os.remove(test_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
