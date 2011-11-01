import track
from track.common import aggregate_sql_rows

feature_fields = ('start', 'end', 'name', 'score', 'strand')
signal_fields = ('start', 'end', 'name', 'score', 'strand')
relational_fields = ('start', 'end', 'name', 'score', 'strand', 'attributes', 'group', 'id')

with track.load('samples/sql/gtf_saccer.sql') as t:
    for chrom in t:
        features = t.read(chrom, feature_fields)
        features = aggregate_sql_rows(features, feature_fields, 'attributes')
        # Do what you need to do to build the JSON after this #
        for i in xrange(10): print features.next(), '\n'
        break
