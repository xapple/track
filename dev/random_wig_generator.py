def random_track(kind='fixed', chrs=16, number_of_regions=32, orig_start=0, length=100, score=1000, jump=50000):
    import random
    chr = 0
    if kind == 'fixed':
        yield 'track type=wiggle_0 name="Pol2 Signal" description="Chip-Seq" source="Random generator"\n'
        for i in xrange(number_of_regions):
            if i % (number_of_regions / chrs) == 0:
                chr += 1
                end  = orig_start
            start = end   + (random.randint(0,jump))
            end   = start + (random.randint(1,length))
            multiplier = random.randint(1,score)
            yield 'fixedStep chrom=chr' + str(chr) + ' start=' + str(start) + ' step=1' + '\n'
            for x in xrange((end - start)):
                yield str(multiplier + multiplier * random.random()) + '\n'
            for x in xrange((end - start)/2):
                yield '0\n'
            end   = start + (random.randint(1,length))
            multiplier = random.randint(1,score)
            constant = str(multiplier + multiplier * random.random())
            for x in xrange((end - start)):
                yield constant + '\n'
    if kind == 'variable':
        yield 'track type=wiggle_0 name="Rap1 Peaks" description="Chip-Seq" source="Random generator"\n'
        for i in xrange(number_of_regions*2):
            if i % ((number_of_regions*2) / chrs) == 0:
                chr += 1
                end  = orig_start
                yield 'variableStep chrom=chr' + str(chr) + '\n'
            start = end   + (random.randint(0,jump))
            end   = start + (random.randint(1,int(length/2)))
            multiplier = random.randint(1,score)
            for x in xrange(start,end):
                yield str(x) + ' ' + str(multiplier + multiplier * random.random()) + '\n'

for line in random_track(): print line

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
