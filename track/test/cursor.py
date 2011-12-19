"""
Contains tests where the cursor of the track is used to execute
SQL statements out of the control of the library.
"""

# Internal modules #
import track
from track.common import temporary_path

# Unittesting module #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class TestNewTables(unittest.TestCase):
    def runTest(self):
        out_path = temporary_path('.sql')
        with track.new(out_path) as t:
            for chrom in range(5): t.write(str(chrom), [(0,10,'A',0.0,-1)])
            cur = t.cursor()
            cur.execute("CREATE table tmp (koopa text,troopa text)")
            cur.execute("INSERT into  tmp values (?,?)", (1,2))

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
