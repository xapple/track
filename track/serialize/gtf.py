"""
This module implements the GTF serialization.
"""

# Internal modules #
from track.serialize import Serializer
from track.util import int_to_strand

# Constants #
all_fields = ['source', 'feature', 'start', 'end', 'score', 'strand', 'frame', 'gene_id', 'transcript_id']
defaults   = ['.', '.', -1, -1, 0.0, '.', '.', '.', '""', '""']


################################################################################
class SerializerGTF(Serializer):
    format = 'gtf'

    def __enter__(self):
        self.file = open(self.path, 'w')
        self.indices = None
        return self

    def __exit__(self, errtype, value, traceback):
        self.file.close()

    def defineFields(self, fields):
        self.indices = []
        # Store all column names (including custom attributes) #
        self.fields = fields
        for f in all_fields:
            try: self.indices.append(fields.index(f))
            except ValueError: self.indices.append(-1)
        # Store non-mandatory fields (everything after "transcript_id") #
        for idx_extra in range(9, len(fields)):
            self.indices.append(idx_extra)

    def newTrack(self, info=None, name=None):
        if not info: info = {}
        info['type'] = 'gtf'
        info['converted_by'] = __package__
        self.file.write("track " + ' '.join([k + '="' + v + '"' for k, v in info.items()]) + '\n')
        self.tracks.append(self.path)

    def newFeature(self, chrom, feature):
        # function to obtain attribute column key-value string
        def attribute_str(key, value):
            return '%s "%s";' % (key, value)
        # Put the fields in the right order #
        # GTF entries always have 8 columns (excluding the seqname column)
        line = range(8)
        for n, i in enumerate(self.indices):
            # i == -1 indicates we should use the default value #
            if i == -1:
                if n < 7:
                    # Everything before the attribute column #
                    line[n] = defaults[n]
                elif n == 7:
                    # "gene_id" annotation #
                    line[n] = attribute_str(self.fields[n], defaults[n])
                elif n == 8:
                    # "transcript_id annotation #
                    attr = attribute_str(self.fields[n], defaults[n])
                    line[7] = '%s %s' % (line[7], attr)
                else:
                    # Annotations of the attribute columns without defaults #
                    raise ValueError("Default value for the %r attribute "
                            "column is not defined." % self.fields[n])
            else:
                if n < 7:
                    line[n] = feature[i]
                elif n == 7:
                    # "gene_id" annotation #
                    line[n] = attribute_str(self.fields[n], feature[i])
                else:
                    # Everything after the "gene_id" annotation #
                    attr = attribute_str(self.fields[n], feature[i])
                    line[7] = '%s %s' % (line[7], attr)

        # Convert the strand #
        line[5] = int_to_strand(line[5])
        # Convert the frame #
        if line[6] == '' or line[6] == None: line[6] = '.'
        # Make sure eveything is a string #
        line = [str(f) for f in line]
        # Write one line #
        self.file.write('\t'.join([chrom] + line) + '\n')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
