"""
Provides easy read/write access to genomic tracks in a fashion that is independent from the underlying format.
Currently the following formats are implemented:

* Bio SQLite (http://bbcf.epfl.ch/twiki/bin/view/BBCF/SqLite)
* BED        (http://genome.ucsc.edu/FAQ/FAQformat.html#format1)
* WIG        (http://genome.ucsc.edu/goldenPath/help/wiggle.html)
* bedGraph   (http://genome.ucsc.edu/goldenPath/help/bedgraph.html)
* bigWig     (http://genome.ucsc.edu/goldenPath/help/bigWig.html)

More formats can be added easily.

To get access to the information contained inside already existing tracks, you would do the following whatever the format of the track is::

    import track
    with track.load('tracks/rp_genes.bed') as rpgenes:
        data = rpgenes.read('chr3')

If your track is in a format that is missing chromosome information (such as the length of every chromosome), you can supply an assembly name or a chromosome file::

    import track
    with track.load('tracks/yeast_genes.bed', chrmeta='sacCer2') as saccer:
        data = saccer.read('chr4')
    with track.load('tracks/yeast_genes.bed', chrmeta='tracks/chrs/yeast.chr') as saccer:
        data = saccer.read('chr4')

For instance, the cumulative base coverage of features on chromosome two can be calculated like this::

    import track
    with track.load('tracks/yeast_genes.sql') as genes:
        # f[1] is the end coordinate and f[0] is the start coordinate
        base_coverage = sum([f[1] - f[0] for f in genes.read('chr2')])

To create a new track and then write to it, you would do the following::

    import track
    with track.new('tracks/rap1_peaks.sql', 'sql', name='Rap1 Peaks') as mypeaks:
        mypeaks.write('chr1', [(10, 20, 'A', 0.0, 1)])

For instance, to make a new track from an old one, and invert the strand of every feature::

    import track
    def invert_strands(data):
        for feature in data:
            yield (feature[0], feature[1], feature[2], feature[3], feature[4] == 1 and -1 or 1)
    with track.load('tracks/orig.sql', name='Normal strands') as a:
        with track.new('tracks/inverted.sql', name='Inverted strands') as b:
            for chrom in a:
                b.write(chrom, invert_strands(a.read(chrom)))

To convert a track from a format (e.g. BED) to an other format (e.g. SQL) you first load the track and call the save_as method on it::

    import track
    with track.load('tracks/rp_genes.bed') as rpgenes:
        rpgenes.save_as('tracks/rp_genes.sql')

To set the chromosome metadata or the track metadata you simply assign to that attribute::

    import track
    with track.load('tracks/scores.sql') as t:
        t.chrmeta    = ``{'chr1': {'length': 197195432}, 'chr2': {'length': 129993255}}``
        t.attributes = {'datatype': 'quantitative', 'source': 'UCSC'}
"""

# Public variables #
__version__ = '1.0.0'
__all__ = ['load', 'new', 'convert']

# Built-in modules #
import os, sqlite3

# Internal modules #
from track.parse import get_parser
from track.serialize import get_serializer
from track.util import determine_format, join_read_queries, read_chr_file
from track.common import check_path, empty_file, empty_sql_file, temporary_path, JournaledDict, natural_sort

# Constants #
special_tables = ['attributes', 'chrNames', 'types']
default_fields = ['start', 'end', 'name', 'score', 'strand']
signal_fields  = ['start', 'end', 'score']
field_types = {
    'start':        'integer',
    'end':          'integer',
    'score':        'real',
    'strand':       'integer',
    'name':         'text',
    'thick_start':  'integer',
    'thick_end':    'integer',
    'item_rgb':     'text',
    'block_count':  'integer',
    'block_sizes':  'text',
    'block_starts': 'text',
    'attributes':   'text',
}

################################################################################
def load(path, format=None, readonly=False):
    """Loads a track from disk, whatever the format is.

        * *path* is the path to track file to load.
        * *format* is an optional string specifying the format of the track to load when it cannot be guessed from the file extension.
        * *readonly* is an optional boolean variable that defaults to ``False``. When set to ``True``, any operation attempting to write to the track will silently be ignored.

    Examples::

        import track
        with track.load('tracks/rp_genes.sql') as rpgenes:
            data = rpgenes.read()
        with track.load('tracks/yeast_data_01', 'sql', 'S. cer. genes') as yeast:
            data = yeast.read()
        with track.load('tracks/repeats.bed', readonly=True) as repeats:
            data = repeats.read()

    ``load`` returns a Track instance.
    """
    # Guess the format #
    if not format: format = determine_format(path)
    # If sql, just make a track with the path #
    # Otherwise we need to convert the file #
    if format == 'sql':
        return Track(path, readonly)
    else:
        sql_path = temporary_path(".sql") or os.path.splitext(path)[0] + ".sql"
        convert(source=(path, format), destination=(sql_path, 'sql'))
        return Track(sql_path, readonly, orig_path=path, orig_format=format)

#---------------------------------------------------------------------------------#
def new(path, format=None):
    """Creates a new empty track in preparation for writing to it.

        * *path* is the path to track file to create.
        * *format* is an optional string specifying the format of the track to load when it cannot be guessed from the file extension.
        * *fields* is an optional

    Examples::

        import track
        with track.new('tmp/track.sql') as t:
            t.write('chr1', [(10, 20, 'Gene A', 0.0, 1)])
            t.save()
        with track.new('tracks/peaks.sql', 'sql', name='High affinity peaks') as t:
            t.write('chr5', [(500, 1200, 'Peak1', 11.3, 0)])
        with track.new('tracks/scores.sql', 'sql', chrmeta='sacCer2' datatype='quantitative',) as t:
            t.write('chr1', [(10, 20, 500.0)])

    ``new`` returns a Track instance.
    """
    # Guess the format #
    if not format: format = os.path.splitext(path)[1][1:]
    check_path(path)
    # If sql, just make a new track at the path #
    # Otherwise we need to make a temporary sql #
    if format == 'sql':
        empty_sql_file(path)
        return Track(path)
    else:
        sql_path = temporary_path(".sql") or os.path.splitext(path)[0] + ".sql"
        empty_file(path)
        empty_sql_file(sql_path)
        return Track(sql_path, orig_path=path, orig_format=format)

#---------------------------------------------------------------------------------#
def convert(source, destination):
    """Converts a track from one format to an other.

        * *source* is the path to the original track to load.
        * *destination* is the path to the track to be created.

    The *source* file should have a different format from the *destination* file.
    If either the source or destination are missing a file extension, you can specify
    their formats using a tuple. See examples below.

    Examples::

        import track
        track.convert('tracks/genes.bed', 'tracks/genes.sql')
        track.convert(('tracks/no_extension', 'gff'), 'tracks/genes.sql')
        track.convert(('tmp/4afb0edf', 'bed'), ('tmp/converted', 'wig'))

    ``convert`` returns the path to the track created or a list of track paths in the case of multi-track files.
    """
    # Parse the source parameter #
    if isinstance(source, tuple):
        source_path   = source[0]
        source_format = source[1]
    else:
        source_path   = source
        source_format = determine_format(source)
    # Parse the destination parameter #
    if isinstance(source, tuple):
        destination_path   = destination[0]
        destination_format = destination[1]
    else:
        destination_path   = destination
        destination_format = os.path.splitext(destination)[1][1:]
    # Check it is not taken #
    check_path(destination_path)
    # Get a serializer #
    serializer = get_serializer(destination_path, destination_format)
    # Get a parser #
    parser = get_parser(source_path, source_format)
    # Do it #
    return parser(serializer)

################################################################################
class Track(object):
    """Once a track is loaded you have access to the following attributes:

       * *fields* is a list the value types that each feature in the track will contain. For instance:
            ``['start', 'end', 'name', 'score', 'strand']``
       * *chromosomes* is a list of all available chromosome. For instance:
            ``['chr1, 'chr2', 'chr3', 'chr4', 'chr5', 'chrC', 'chrM']``
       * *chrmeta* is a dictionary of meta data associated to each chromosome (information like length, etc). For instance:
            ``{'chr1': {'length': 197195432}, 'chr2': {'length': 129993255}}``
       * *attributes* is a dictionary of meta data associated to the track (information like the source, etc). For instance:
             ``{'datatype': 'signal', 'source': 'SGD'}``

    The track object itself is iterable and will yield the name of all chromosomes.

    Examples::

        import track
        with track.load('tracks/all_genes.sql') as genes:
            for chrom in genes: print chrom
            if 'chrY' in genes: print 'Male'
            if len(genes) != 23: print 'Aneuploidy'
    """

    def __init__(self, path, readonly=False, autosave=False, orig_path=None, orig_format=None):
        # Passed attributes #
        self.path        = path
        self.readonly    = readonly
        self.autosave    = autosave
        self.orig_path   = orig_path
        self.orig_format = orig_format
        # Other attributes #
        self.modified   = False
        # Stuff to do #
        self._chrmeta    = JournaledDict()
        self._attributes = JournaledDict()

    def __enter__(self):
        return self

    def __exit__(self, errtype, value, traceback):
        self.close()

    def __iter__(self):
        return iter(self.chromosomes)

    def __len__(self):
        return len(self.chromosomes)

    def __contains__(self, key):
        return key in self.chromosomes

    @property
    def fields(self):
        if self.chrs_from_tables: return self.get_fields_of_table(self.chrs_from_tables[0])
        else:                     return []
        return [x[1] for x in self.cursor.execute('pragma table_info("' + table + '")').fetchall()]

    @property
    def tables(self):
        self.cursor.execute("select name from sqlite_master where type='table'")
        return [x[0].encode('ascii') for x in self.cursor.fetchall()]

    @property
    def chromosomes(self):
        chroms = [x for x in self.tables if x not in special_tables and not x.endswith('_idx')]
        chroms.sort(key=natural_sort)
        return chroms

    #-----------------------------------------------------------------------------#
    def save(self):
        """Stores the changes that were applied to the track on the disk. If the track was loaded from a text file such as 'bed', the file is rewritten with the changes included. If the track was loaded as an SQL file, the changes are committed to the database.

       Examples::

           import track
           with track.load('tracks/rp_genes.bed') as t:
               t.remove('chr19_gl000209_random')
               t.save()

       ``save`` returns nothing but the original file on the disk is modified.
        """
        if self.attributes.modified: self.attributes_write()
        if self.chrmeta.modified: self.chrmeta_write()
        self.make_missing_tables()
        self.make_missing_indexes()
        self.connection.commit()

    #-----------------------------------------------------------------------------#
    def rollback(self):
        """Reverts all changes to the track since the last call to ``save()``.

        Examples::

           import track
           with track.load('tracks/rp_genes.bed') as t:
               t.remove('chr19_gl000209_random')
               t.export('tmp/clean.bed')
               t.rollback()

       ``rollback`` returns nothing but the track is reverted.
        """
        self.connection.rollback()

    #-----------------------------------------------------------------------------#
    def close(self):
        """Closes the current track. This method is useful when you are not using the 'with ... as' form for loading tracks.

        Examples::

            import track
            t = track.load('tracks/rp_genes.bed')
            t.remove('chr19_gl000209_random')
            t.save()
            t.close()

        ``close`` returns nothing but the track it is called on is closed.
        """
        if self.autosave: self.save()
        self.cursor.close()
        self.connection.close()

    #-----------------------------------------------------------------------------#
    def export(self, path, format=None):
        """Exports the current track to a given format.

        * *path* is the path to track file to create.
        * *format* is an optional string specifying the format of the track to load when it cannot be guessed from the file extension.

        Examples::

            import track
            with track.load('tracks/rp_genes.bed') as t:
                t.remove('chr19_gl000209_random')
                t.export('tmp/clean.bed')
                t.rollback()

        ``export`` returns nothing but a new file is created at the specified path. The current track object is unchanged.
        """
        # Check it is not taken #
        check_path(path)
        # Get a serializer #
        serializer = get_serializer(path, format)
        # Get a parser #
        parser = get_parser(self, 'track')
        # Do it #
        return parser(serializer)

    #-----------------------------------------------------------------------------#
    def read(self, selection=None, fields=None, order='start,end', cursor=False):
        """Reads data from the genomic file.

        * *selection* can be several things.

        *selection* can be the name of a chromosome, in which case all the data on that chromosome will be returned.

        *selection* can also be a dictionary specifying: regions, score intervals or strands. Indeed, you can specify a region in which case only features contained in that region will be returned. You can also input a tuple specifying a score interval in which case only features contained in those score boundaries will be returned. You can even specify a strand. The dictionary can contain one or several of these arguments. See examples for more details.

        Adding the parameter ``'inclusion':'strict'`` to a region dictionary will return only features exactly contained inside the interval instead of features simply included in the interval.

        To combine multiple selections you can specify a list including chromosome names and region dictionaries. As expected, if such is the case, the joined data from those selections will be returned with an added 'chr' field in front since the results may span several chromosomes. When *selection* is left empty, the data from all chromosome is returned.

        * *fields* is a list of fields which will influence the length of the tuples returned and the way in which the information is returned. The default for quantitative tracks is ``['start', 'end', 'name', 'score', 'strand']`` and ``['start', 'end', 'score']`` for quantitative tracks.

        * *order* is a sublist of *fields* which will influence the order in which the tuples are yielded. By default results are sorted by ``start`` and, secondly, by ``end``.

        * *cursor* is a boolean which should be set true if you are performing several operations on the same track at the same time. This is the case, for instance when you are chaining a read operation to a write operation.

        Examples::

            import track
            with track.load('tracks/example.sql') as t:
                data = t.read()
                data = t.read('chr2')
                data = t.read('chr3', ['name', 'strand'])
                data = t.read(['chr1','chr2','chr3'])
                data = t.read({'chr':'chr1', 'start':100})
                data = t.read({'chr':'chr1', 'start':10000, 'end':15000})
                data = t.read({'chr':'chr1', 'start':10000, 'end':15000, 'inclusion':'strict'})
                data = t.read({'chr':'chr1', 'strand':1})
                data = t.read({'chr':'chr1', 'score':(10,100)})
                data = t.read({'chr':'chr1', 'start':10000, 'end':15000, 'strand':-1, 'score':(10,100)})
                data = t.read({'chr':'chr5', 'start':0, 'end':200}, ['strand', 'start', 'score'])
            # Duplicate a chromosome
            with track.load('tracks/copychrs.sql') as t:
                t.write('chrY', t.read('chrX', cursor=True))
                t.save()

        ``read`` returns a generator object yielding tuples.
        """
        # Default selection #
        if not selection: selection = self.chrs_from_tables
        # Case list of things #
        if isinstance(selection, (list, tuple)):
            return join_read_queries(self, selection, fields)
        # Case chromosome name #
        elif isinstance(selection, basestring): chrom = selection
        # Case selection dictionary #
        elif isinstance(selection, dict): chrom = selection['chr']
        # Other cases #
        else: raise TypeError, 'The following selection parameter: "' + selection + '" was not understood'
        # Empty chromosome case #
        if chrom not in self.chrs_from_tables: return ()
        # Default columns #
        columns = fields and fields[:] or self.get_fields_of_table(chrom)
        # Make the query #
        sql_request = "select " + ','.join(columns) + " from '" + chrom + "'"
        if isinstance(selection, dict): sql_request += " where " + make_cond_from_sel(selection)
        order_by = 'order by ' + order
        # Return the results #
        if cursor: cur = self.connection.cursor()
        else:      cur = self.cursor
        return cur.execute(sql_request + ' ' + order_by)

    #-----------------------------------------------------------------------------#
    def write(self, chrom, data, fields=None):
        """Writes data to a genomic file.

        * *chrom* is the name of the chromosome on which one wants to write. For instance, if one is using the BED format this will become the first column, while if one is using the SQL format this will become the name of the table to be created.

        * *data* must be an iterable object that yields tuples of the correct length. As an example, the ``read`` function of this class produces such objects.

        * *fields* is a list of fields which will influence the number of columns for every feature in the file and hence the length of the tuples to be generated. The value of *fields* should not change within the same track.

        Examples::

            import track
            with track.load('tracks/example.sql') as t:
                t.write('chr1', [(10, 20, 'A', 0.0, 1), (40, 50, 'B', 0.0, -1)])
                def example_generator():
                    for i in xrange(5):
                        yield (10, 20, 'X', i, 1)
                t.write('chr2', example_generator())
                t.save()

        ``write`` returns nothing.
        """
        self.modified = True
        if self.readonly: return
        # Default fields #
        if self.datatype == 'quantitative': fields = Track.quantitative_fields
        if not fields:                      fields = Track.qualitative_fields
        # Maybe create the table #
        if chrom not in self.chrs_from_tables:
            columns = ','.join([field + ' ' + Track.field_types.get(field, 'text') for field in fields])
            self.cursor.execute('create table "' + chrom + '" (' + columns + ')')
        # Execute the insertion
        sql_command = 'insert into "' + chrom + '" (' + ','.join(fields) + ') values (' + ','.join(['?' for x in range(len(fields))])+')'
        try:
            self.cursor.executemany(sql_command, data)
        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as err:
            raise Exception("The command '" + sql_command + "' on the database '" + self.path + "' failed with error: '" + str(err) + "'" + \
                '\n    ' + 'The bindings: ' + str(fields) + \
                '\n    ' + 'You gave: ' + str(data))

    #-----------------------------------------------------------------------------#
    def remove(self, chrom=None):
        """Removes data from a given chromosome.

        * *chrom* is the name of the chromosome that one wishes to delete or a list of chromosomes to delete.

        Called with no arguments, will remove every chromosome.

        Examples::

            import track
            with track.load('tracks/example.sql') as t:
                t.remove('chr1')
                t.save()
            with track.load('tracks/example.sql') as t:
                t.remove(['chr1', 'chr2', 'chr3'])
                t.save()
            with track.load('tracks/example.sql') as t:
                t.remove()
                t.save()

        ``remove`` returns nothing.
        """
        self.modified = True
        if self.readonly: return
        if not chrom:
            chrom = self.chrs_from_tables
        if isinstance(chrom, list):
            for ch in chrom: self.remove(ch)
        else:
            self.cursor.execute("DROP table '" + chrom + "'")
            if chrom in self.chrmeta: self.chrmeta.pop(chrom)

    #-----------------------------------------------------------------------------#
    def rename(self, previous_name, new_name):
        """Renames a chromosome from *previous_name* to *new_name*

        Examples::

            import track
            with track.load('tracks/rp_genes.bed') as t:
                t.rename('chr4', 'chrIV')
                t.save()

        ``rename`` returns nothing.
        """
        self.modified = True
        if self.readonly: return
        if previous_name not in self.chrs_from_tables: raise Exception("The chromosome '" + previous_name + "' doesn't exist.")
        self.cursor.execute("ALTER TABLE '" + previous_name + "' RENAME TO '" + new_name + "'")
        self.cursor.execute("drop index IF EXISTS '" + previous_name + "_range_idx'")
        self.cursor.execute("drop index IF EXISTS '" + previous_name + "_score_idx'")
        self.cursor.execute("drop index IF EXISTS '" + previous_name + "_name_idx'")
        if previous_name in self.chrmeta:
            self.chrmeta[new_name] = self.chrmeta[previous_name]
            self.chrmeta.pop(previous_name)
        self.chrs_from_tables

    #-----------------------------------------------------------------------------#
    def count(self, selection=None):
        """Counts the number of features or entries in a given selection.

        * *selection* is the name of a chromosome, a list of chromosomes, a particular span or a list of spans. In other words, a value similar to the *selection* parameter of the *read* method.

        Called with no arguments, will count every feature in a track.

        Examples::

            import track
            with track.load('tracks/example.sql') as t:
                num = t.count('chr1')
            with track.load('tracks/example.sql') as t:
                num = t.count(['chr1','chr2','chr3'])
            with track.load('tracks/example.sql') as t:
                num = t.count({'chr':'chr1', 'start':10000, 'end':15000})

        ``count`` returns an integer.
        """
        # Default selection #
        if not selection:
            selection = self.chrs_from_tables
        # Case several chromosome #
        if isinstance(selection, list) or isinstance(selection, tuple):
            return sum([self.count(s) for s in selection])
        # Case chromosome name #
        elif isinstance(selection, basestring):
            if selection not in self.chrs_from_tables: return 0
            sql_request = "select COUNT(*) from '" + selection + "'"
        # Case span dictionary #
        elif isinstance(selection, dict):
            chrom = selection['chr']
            if chrom not in self.chrs_from_tables: return 0
            sql_request = "select COUNT(*) from '" + chrom + "' where " + make_cond_from_sel(selection)
        # Other cases #
        else: raise TypeError, 'The following selection parameter: "' + selection + '" was not understood'
        # Return the results #
        return self.cursor.execute(sql_request).fetchone()[0]

    #-----------------------------------------------------------------------------#
    def ucsc_to_ensembl(self):
        """Converts all entries of a track from the UCSC standard to the Ensembl standard effectively adding one to every start position.

       Examples::

           import track
           with track.load('tracks/example.sql') as t:
               t.ucsc_to_ensembl()

       ``ucsc_to_ensembl`` returns nothing.
        """
        for chrom in self.chrs_from_tables: self.cursor.execute("update '" + chrom + "' set start=start+1")

    def ensembl_to_ucsc(self):
        """Converts all entries of a track from the Ensembl standard to the UCSC standard effectively subtracting one from every start position.

       Examples::

           import track
           with track.load('tracks/rp_genes.bed') as t:
               t.ensembl_to_ucsc()

       ``ensembl_to_ucsc`` returns nothing.
        """
        for chrom in self.chrs_from_tables: self.cursor.execute("update '" + chrom + "' set start=start-1")

    #-----------------------------------------------------------------------------#
    def get_score_vector(self, chrom):
        """Returns an iterable with as many elements as there are base pairs in the chromosomes specified by the *chrom* parameter. Every element of the iterable is a float indicating the score at that position. If the track has no score associated, ones are inserted where features are present.

            * *chrom* is the name of the chromosome on which one wants to create a score vector from.

        Examples::

            import track
            with track.new('tmp/track.sql') as t:
                scores = t.vector('chr1')

        ``get_score_vector`` returns an iterable yielding floats.
        """
        # Conditions #
        if 'score' not in self.fields:
            def add_ones(X):
                for x in X: yield x + (1.0,)
            data = add_ones(self.read(chrom, ['start','end']))
        else:
            data = self.read(chrom, ['start','end','score'])
        # Initialization #
        last_end = 0
        x = (-1,0)
        # Core loop #
        for x in data:
            for i in xrange(last_end, x[0]): yield 0.0
            for i in xrange(x[0],     x[1]): yield x[2]
            last_end = x[1]
        # End piece #
        if self.chrmeta.get(chrom):
            for i in xrange(x[1], self.chrmeta[chrom]['length']): yield 0.0

    #-----------------------------------------------------------------------------#
    def roman_to_integer(self, names=None):
        """Converts the name of all chromosomes from the roman numeral standard to the arabic numeral standard. For instance, 'chrI' will become 'chr1' while 'chrII' will become 'chr2', etc.

        Examples::

            import track
            with track.new('tmp/track.sql') as t:
                scores = t.roman_to_integer()

        ``roman_to_integer`` returns nothing.
        """
        names = names or {'chrM':'chrQ', '2micron':'chrR'}
        def convert(chrom):
            if chrom in names: return names[chrom]
            match = re.search('([a-zA-Z]*?)([IVX]+)$', chrom)
            return match.group(1) + str(roman_to_int(match.group(2)))
        for chrom in self: self.rename(chrom, convert(chrom))

    def integer_to_roman(self, names=None):
        """Converts the name of all chromosomes from the arabic numeral standard to the roman numeral standard. For instance, 'chr1' will become 'chrI' while 'chr2' will become 'chrII', etc.

        Examples::

            import track
            with track.new('tmp/track.sql') as t:
                scores = t.roman_to_integer()

        ``integer_to_roman`` returns nothing.
        """
        names = names or {'chrQ':'chrM', 'chrR':'2micron'}
        def convert(chrom):
            if chrom in names: return names[chrom]
            match = re.search('([a-zA-Z]*)([0-9]+)$', chrom)
            return match.group(1) + int_to_roman(int(match.group(2)))
        for chrom in self: self.rename(chrom, convert(chrom))

    #-----------------------------------------------------------------------------#
    def set_chrmeta(self, spiece=None, chrfile=None):
        """Set the chromosome metadata of the track. This method can be called with no arguments, in which case the spiece name using information from the GenRep server. This method can also be called directly with a GenRep compatible spiece name. Finally, one can call this method by specifying a chromosome file, containing

        * *spiece* is the name of a chromosome, a list of chromosomes, a particular span or a list of spans. In other words, a value similar to the *selection* parameter of the *read* method.
        * *chrfile* is the name of a chromosome, a list of chromosomes, a particular span or a list of spans. In other words, a value similar to the *selection* parameter of the *read* method.

        Of course, genomic formats such as ``bed`` cannot store this kind of meta data. Hence, when loading tracks in these text formats, this information is lost once the track is closed.

        Examples::

            import track
            track.convert('tracks/genes.bed', 'tracks/genes.sql')
            with track.load('tracks/genes.sql') as t:
                t.set_chrmeta('sacCer')
                t.save()

        ``set_chrmeta`` returns nothing but the self.chrmeta variable is modified.
        """
        if os.path.isfile(chrfile):
            self.chrmeta = read_chr_file(chrfile)
        if spiece:
            self.chrmeta = genrep.get_chrmeta(spiece)
        else:
            spiece = genrep.guess_spiece(self.chromosomes)
            self.chrmeta = genrep.get_chrmeta(spiece)

    def _chrmeta_read(self):
        """Populates the self._chrmeta attribute with information found in the 'chrNames' table."""
        self._chrmeta = JournaledDict()
        if not 'chrNames' in self.tables: return
        self.cursor.execute("pragma table_info(chrNames)")
        column_names = [x[1].encode('ascii') for x in self.cursor.fetchall()]
        all_rows = self.cursor.execute("select * from chrNames").fetchall()
        return column_names, all_rows

    def _chrmeta_write(self):
        """Rewrites the 'chrNames' table so that it reflects the contents of the self._chrmeta attribute."""
        if self.readonly: return
        self.cursor.execute('drop table IF EXISTS chrNames')
        if self.chrmeta:
            self.cursor.execute('create table chrNames (name text, length integer)')
            for r in self.chrmeta.rows: self.cursor.execute('insert into chrNames (' + ','.join(r.keys()) + ') values (' + ','.join(['?' for x in r.keys()])+')', tuple(r.values()))

    @property
    def chrmeta(self):
        return self._chrmeta

    @chrmeta.setter
    def chrmeta(self, value):
        self._chrmeta.overwrite(value)

    #--------------------------------------------------------------------------#
    def _attributes_read(self):
        if not 'attributes' in self.all_tables: return {}
        self.cursor.execute("select key, value from attributes")
        return dict(self.cursor.fetchall())

    def _attributes_write(self):
        if self.readonly: return
        self.cursor.execute('drop table IF EXISTS attributes')
        if self.attributes:
            self.cursor.execute('create table attributes (key text, value text)')
            for k in self.attributes.keys(): self.cursor.execute('insert into attributes (key,value) values (?,?)', (k, self.attributes[k]))

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        self._attributes.overwrite(value)

    #--------------------------------------------------------------------------#
    @property
    def datatype(self):
        # Next line is a hack to remove a new datatype introduced by GDV - remove at a later date #
        if self.attributes.get('datatype') == 'QUALITATIVE_EXTENDED': return 'qualitative'
        # End hack #
        return self.attributes.get('datatype', '').lower()

    @datatype.setter
    def datatype(self, value):
        if value not in ['quantitative', 'qualitative']:
            raise Exception("The datatype you are trying to use is invalid: '" + str(value) + "'.")
        self.attributes['datatype'] = value

    @property
    def name(self):
        return self.attributes.get('name', 'Unnamed')

    @name.setter
    def name(self, value):
        self.attributes['name'] = value

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
