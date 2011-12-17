"""
Contains chained write tests.
"""

# Built-in modules #
import os, shutil

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
class TestChain(unittest.TestCase):
    """Chain a read to a write"""
    def runTest(self):
        in_path = samples['small_signals'][7]['sql']
        out_path = temporary_path('.sql')
        with track.load(in_path) as i:
            with track.new(out_path) as o:
                for chrom in i: o.write(chrom, i.read(chrom))
                self.assertEqual(list(o.read('chrI')), list(i.read('chrI')))
        os.remove(out_path)

#---------------------------------------------------------------------------------#
class TestMissingFields(unittest.TestCase):
    """Write with missing fields"""
    def runTest(self):
        in_path = samples['small_features'][1]['sql']
        out_path = temporary_path('.sql')
        chrom = 'chrI'
        with track.load(in_path) as i:
            with track.new(out_path) as o:
                o.fields = track.default_fields
                o.write(chrom, i.read(chrom, ('start','end')))
                got = tuple(o.read(chrom).next())
                expected = (0, 10, None, None, None)
        self.assertEqual(got, expected)
        os.remove(out_path)

#---------------------------------------------------------------------------------#
class TestBindings(unittest.TestCase):
    """Tracking down a bug relating to binding numbers"""
    def runTest(self):
        old_path = samples['small_features'][1]['sql']
        new_path = temporary_path('.sql')
        shutil.copyfile(old_path, new_path)
        old_table = 'chrI'
        new_table = 'tmp_chrI'
        query = 'CREATE table "%s" (id text, subs text, foreign key(id) references "%s" (id));'
        data = [('abc','def'),('ghi','jkl')]
        with track.load(new_path) as t:
           t.cursor.execute(query % (new_table, old_table))
           t.write(new_table, data, ('id', 'subs'))
           got = map(tuple, t.read(new_table, order=None))
        self.assertEqual(got, data)
        os.remove(new_path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
