"""
This module implements the parsing of BED files.

http://genome.ucsc.edu/FAQ/FAQformat.html#format1
"""

# Built-in modules #
import shlex

# Internal modules #
from track.parse import Parser
from track.common import iterate_lines, get_next_item

################################################################################
class ParserWIG(Parser):
    def parse(self):
        # Initial variables #
        info   = {}
        params = {}
        declare_track = True
        last_feature  = None
        last_chrom    = None
        # Line loop #
        for number, line in iterate_lines(self.path):
            # Ignored lines #
            if line.startswith("browser "): continue
            # Track headers #
            if line.startswith("track "):
                try:
                    info = dict([p.split('=',1) for p in shlex.split(line[6:])])
                except ValueError:
                    self.handler.error("The track%s seems to have an invalid <track> header line", self.path, number)
                declare_track = True
                continue
            # Have we started a track already ? #
            if declare_track:
                declare_track = False
                if last_feature:
                    self.handler.newFeature(last_chrom, last_feature)
                    last_feature = None
                    last_chrom   = None
                self.handler.newTrack(info, self.name)
                self.handler.defineFields(['start', 'end', 'score'])
            # Directive line #
            if line.startswith("variableStep") or line.startswith("fixedStep"):
                params = dict([p.split('=',1) for p in shlex.split('mode=' + line)])
                if not params.get('chrom', False):
                    self.handler.error("The track%s doesn't specify a chromosome.", self.path, number)
                try:
                    params['span'] = int(params.get('span', 1))
                except ValueError:
                    self.handler.error("The track%s has a non integer as span value.", self.path, number)
                if params['span'] < 1:
                    self.handler.error("The track%s has a negative or null span value.", self.path, number)
                if line.startswith("fixedStep "):
                    if not 'start' in params:
                       self.handler.error("The track%s has a fixedStep directive without a start.", self.path, number)
                    try:
                        params['start'] = int(params['start'])
                    except ValueError:
                         self.handler.error("The track%s has a non integer as start value.", self.path, number)
                    try:
                        params['step'] = int(params.get('step',1))
                    except ValueError:
                        self.handler.error("The track%s has a non integer as step value.", self.path, number)
                    if params['step'] < 1:
                        self.handler.error("The track%s has a negative or null step value.", self.path, number)
                    params['count'] = 0
                continue
            # Not a directive line #
            if not params:
                self.handler.error("The track%s is missing a fixedStep or variableStep directive.", self.path, number)
            # Fixed #
            if params['mode'] == 'fixedStep':
                try:
                    line = float(line)
                except ValueError:
                    self.handler.error("The track%s has non floats as score values.", self.path, number)
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
                    self.handler.error("The track%s has invalid values.", self.path, number)
                except IndexError:
                  self.handler.error("The track%s has missing values.", self.path, number)
                chrom   = params['chrom']
                feature = [line[0], line[0] + params['span'], line[1]]
            # Ignore null scores #
            if feature[3] == 0.0: continue
            # Merge adjacent features with same scores #
            # For instance ['chr1', 10, 11, 9.8] and ['chr1', 11, 12, 9.8] should merge.
            if last_feature:
                if last_chrom[0] == chrom[0]:
                    if last_feature[1] > feature[0]:
                        self.handler.error("The track%s has a start or span larger than its end or step.", self.path)
                    if last_feature[1] == feature[0] and last_feature[3] == feature[3]:
                        last_feature[1] = feature[1]
                        continue
                self.handler.newFeature(last_chrom, last_feature)
            last_feature = feature
            last_chrom   = chrom
        if last_feature: self.handler.newFeature(last_chrom, last_feature)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
