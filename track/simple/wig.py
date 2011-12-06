"""
This module implements the simple parsing of WIG files according to this standard:

http://genome.ucsc.edu/goldenPath/help/wiggle.html
"""

# Built-in modules #
import shlex

# Internal modules #
from track.simple import SimpleTrack

###########################################################################
class SimpleWIG(SimpleTrack):
    def read_features(self):
        # Initial variables #
        params = {}
        last_feature  = None
        last_chrom    = None
        # Line loop #
        for number, line in enumerate(self.file):
            # Strip #
            line = line.strip()
            if len(line) == 0: continue
            # Ignored lines #
            if line.startswith("browser "): continue
            if line.startswith("track "):   continue
            if line.startswith("#"):        continue
            # Directive line #
            if line.startswith("variableStep") or line.startswith("fixedStep"):
                params = dict([p.split('=',1) for p in shlex.split('mode=' + line)])
                if not params.get('chrom', False):
                    self.error("The track%s doesn't specify a chromosome.", self.path, number)
                try:
                    params['span'] = int(params.get('span', 1))
                except ValueError:
                    self.error("The track%s has a non integer as span value.", self.path, number)
                if params['span'] < 1:
                    self.error("The track%s has a negative or null span value.", self.path, number)
                if line.startswith("fixedStep "):
                    if not 'start' in params:
                       self.error("The track%s has a fixedStep directive without a start.", self.path, number)
                    try:
                        params['start'] = int(params['start'])
                    except ValueError:
                         self.error("The track%s has a non integer as start value.", self.path, number)
                    try:
                        params['step'] = int(params.get('step',1))
                    except ValueError:
                        self.error("The track%s has a non integer as step value.", self.path, number)
                    if params['step'] < 1:
                        self.error("The track%s has a negative or null step value.", self.path, number)
                    params['count'] = 0
                continue
            # Not a directive line #
            if not params:
                self.error("The track%s is missing a fixedStep or variableStep directive.", self.path, number)
            # Fixed #
            if params['mode'] == 'fixedStep':
                try:
                    line = float(line)
                except ValueError:
                    self.error("The track%s has non floats as score values.", self.path, number)
                base = params['start'] + params['count'] * params['step']
                chrom   = params['chrom']
                feature = [base, base + params['span'], line]
                params['count'] += 1
            # Variable #
            if params['mode'] == 'variableStep':
                line = line.split('\t')
                if len(line) == 1: line = line[0].split()
                try:
                    line[0] = int(line[0])
                    line[1] = float(line[1])
                except ValueError:
                    self.error("The track%s has invalid values.", self.path, number)
                except IndexError:
                  self.error("The track%s has missing values.", self.path, number)
                chrom   = params['chrom']
                feature = [line[0], line[0] + params['span'], line[1]]
            # Ignore null scores #
            if feature[2] == 0.0: continue
            # Merge adjacent features with same scores #
            # For instance ['chr1', 10, 11, 9.8] and ['chr1', 11, 12, 9.8] should merge.
            if last_feature:
                if last_chrom == chrom:
                    if last_feature[1] > feature[0]:
                        self.error("The track%s has a start or span larger than its end or step.", self.path, number)
                    if last_feature[1] == feature[0] and last_feature[2] == feature[2]:
                        last_feature[1] = feature[1]
                        continue
                yield last_chrom, last_feature
            last_feature = feature
            last_chrom   = chrom
        if last_feature: yield last_chrom, last_feature

    def write_features(self, generator):
        for f in generator: yield "fixedStep chrom=%s start=%s span=%s\n%s\n" % (f[0],f[1],f[2]-f[1],f[3])

    #-----------------------------------------------------------------------------#
    @property
    def datatype(self):
        return 'signal'

    def guess_fields(self):
        return ('start', 'end', 'score')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
