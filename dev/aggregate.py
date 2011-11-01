import track
from track.common import agregate_extra_sql_columns

feature_fields = ('start', 'end', 'name', 'score', 'strand')
signal_fields = ('start', 'end', 'name', 'score', 'strand')
relational_fields = ('start', 'end', 'name', 'score', 'strand', 'attributes', 'group', 'id')

with track.load('samples/sql/features1.sql') as t:
    for chrom in t:
        features = t.read(chrom)
        features = agregate_extra_sql_columns(features, feature_fields, 'attributes')
        print list(features)
