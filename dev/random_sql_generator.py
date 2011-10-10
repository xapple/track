# Built-in modules #
import sys, random, tempfile

# Internal modules #
from track.serialize import get_serializer
from track.parse import Parser

# Constants #
feature_factor = 500
chrsuffix = 'Awfully super extra long chromosome denomination string '

################################################################################
class RandomTrack(Parser):
    """
    This module doesn't actually parse a file. It generates a random
    track by inventing features with random names and random positions.
    The scores follow a gamma distribution.
    """

    def parse(self):
        # Initialize #
        chromosomes = [chrsuffix + str(x) for x in range(10)]
        name_generator = tempfile._RandomNameSequence()
        name_generator.rng.seed(0)
        # New track #
        self.handler.newTrack('Random track generator')
        self.handler.defineFields(['start', 'end', 'name', 'score', 'strand'])
        self.handler.defineChrmeta(dict([(ch, dict([('length', sys.maxint)])) for ch in chromosomes]))
        # Lots of features #
        for chrom in chromosomes:
            start = 0
            for feat in range(int(feature_factor + 4*feature_factor*random.random())):
                start = start + (random.randint(0,100))
                end = start + (random.randint(1,100))
                name = name_generator.next()
                score = random.gammavariate(1, 0.1) * 1000
                strand = map(lambda x: x==1 and 1 or -1, [random.randint(0,1)])[0]
                self.handler.newFeature(chrom, (start, end, name, score, strand))

import sys
sql_path = sys.argv[1]
serializer = get_serializer(sql_path, 'sql')
parser = RandomTrack()
print parser(serializer)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
