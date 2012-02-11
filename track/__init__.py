"""
Provides easy read/write access to genomic tracks in a fashion that is independent from the underlying format. Requires Python 2.6 or higher.
Currently the following formats are implemented:

* `BioSQLite <http://bbcf.epfl.ch/twiki/bin/view/BBCF/SqLite>`_
* `BED <http://genome.ucsc.edu/FAQ/FAQformat.html#format1>`_
* `WIG <http://genome.ucsc.edu/goldenPath/help/wiggle.html>`_
* `GFF <http://genome.ucsc.edu/FAQ/FAQformat.html#format3>`_
* `GTF <http://genome.ucsc.edu/FAQ/FAQformat.html#format4>`_
* `bedGraph <http://genome.ucsc.edu/goldenPath/help/bedgraph.html>`_
* `bigWig <http://genome.ucsc.edu/goldenPath/help/bigWig.html>`_

More formats can be added easily.

############
Installation
############

To install you should download the latest source code from GitHub, either by going to::

    http://github.com/xapple/track

and clicking on "Downloads", or by cloning the git repository with::

    $ git clone https://github.com/xapple/track.git

Once you have the source code, run::

    $ cd track
    $ sudo python setup.py install

to install it. If you don't have permission to install it in the default directory, you can simply build the source in-place and use the package from the git repository::

    $ python python setup.py build_ext --inplace

###########
Quick start
###########

To get access to the information contained inside already existing genomic tracks, you would do the following whatever the format of the track is::

    import track
    with track.load('tracks/rp_genes.bed') as rp:
        data = rp.read('chr3')

The ``data`` variable will now yield tuples containing genomic features on chromosome three. Typically, a feature consits of elements such as a start coordinate, a stop coordinate, a name, a score value, and a strand. Hence, when calling ``data.next()`` you will get objects looking something like this: ``(15, 20, 'Gene A', 3.0, 1)``.

However, it is strongly advised to convert your tracks into the SQL format before working with them for better performance. If you do this, your text files will only be parsed once. The previous code becomes::

    import track
    track.convert('tracks/rp_genes.bed', 'tracks/rp_genes.sql')
    with track.load('tracks/rp_genes.sql') as rp:
        data = rp.read('chr3')

Now, let's use our read query for computing something. For instance, the cumulative base coverage of all features on chromosome two can be calculated like this::

    import track
    with track.load('tracks/rp_genes.gff') as rp:
        all_genes = rp.read('chr2')
        base_coverage = sum([gene[1] - gene[0] for gene in all_genes])
        # gene[1] is the end coordinate and gene[0] is the start coordinate

The results coming from the ``read`` function can also be referenced by field name. Hence this code works as well::

    import track
    with track.load('tracks/rp_genes.gff') as rpgenes:
        all_genes = rpgenes.read('chr2')
        base_coverage = sum([gene['end'] - gene['start'] for gene in all_genes])

To create a new track and then write to it, you should use the following::

    import track
    with track.new('tracks/rap1_peaks.sql') as mypeaks:
        mypeaks.write('chr1', [(10, 20, 'Peak A', 0.0, 1)])

To duplicate a chromosome inside the same track, you can use the following::

    with track.load('tracks/copychrs.sql') as t:
        t.write('chrY', t.read('chrX'))

To make a new track from an old one, and invert the strand of every feature::

    import track
    def invert_strands(data):
        for gene in data:
            yield (gene[0], gene[1], gene[2], gene[3], gene[4] == 1 and -1 or 1)
    with track.load('tracks/orig.sql') as orig:
        with track.new('tracks/inverted.sql') as inverted:
            for chrom in orig:
                inverted.write(chrom, invert_strands(orig.read(chrom)))

To convert a track from a format (e.g. BED) to an other format (e.g. GFF) you call the `track.convert` function::

    import track
    track.convert('tracks/rp_genes.bed', 'tracks/rp_genes.gff')

If your track is in a format that is missing chromosome information (such as the length of every chromosome), you can supply an assembly name or a chromosome file::

    import track
    with track.load('tracks/yeast_genes.sql') as t:
        # Specify the assembly
        t.assembly = 'hg19'
        # Or load a tab delimited file
        t.load_chr_file('info/yeast.chr')

To set the chromosome metadata or the track metadata you simply assign to that attribute::

    import track
    with track.load('tracks/scores.sql') as t:
        t.chrmeta = ``{'chr1': {'length': 197195432}, 'chr2': {'length': 129993255}}``
        t.info = {'datatype': 'signal', 'source': 'UCSC'}
"""

b'This module needs Python 2.6 or later.'

# Special variables #
__version__ = '1.0.0'
__all__ = ['load', 'new', 'convert']

# Other variables #
formats = ('bed', 'wig', 'gff', 'gtf', 'bedGraph', 'bigWig')

# Built-in modules #
import os, re, sqlite3
from itertools import imap

# Internal modules #
from track.parse import get_parser
from track.serialize import get_serializer
from track.util import determine_format, join_read_queries, make_cond_from_sel, parse_chr_file
from track.util import sql_field_types, py_field_types, serialize_chr_file
from track.util import gzip_inner_format
from track.common import check_path, check_file, empty_file, empty_sql_file, temporary_path
from track.common import JournaledDict, natural_sort, int_to_roman, roman_to_int
from track.common import Color, pick_iterator_elements, get_next_item, is_gzip
from track.common import if_url_then_get_url
from track.genrep import Assembly

# Compiled modules #
from track.pyrow import SuperRow

# Constants #
special_tables = ('attributes', 'chrNames', 'types')
minimum_fields = ('start', 'end')
default_fields = ('start', 'end', 'name', 'score', 'strand')
signal_fields = ('start', 'end', 'score')
feature_fields = ('start', 'end', 'name', 'score', 'strand', 'attributes')
relational_fields = ('start', 'end', 'name', 'score', 'strand', 'attributes', 'group', 'id')

################################################################################
def load(path, format=None, readonly=False):
    """Loads a track from disk, whatever the format is.

       :param path: is the path to track file to load or an URL. If the path is an URL, the file will be downloaded automatically. If the path is a GZIP file, it will be decompressed automatically.
       :type  path: string
       :param format: is an optional parameter specifying the format of the track to load when it cannot be guessed from the file extension.
       :type  format: string
       :param readonly: is an optional parameter that defaults to ``False``. When set to ``True``, any operation attempting to write to the track will silently be ignored
       :type  readonly: bool
       :returns: a Track instance

       ::

            import track
            with track.load('tracks/rp_genes.bed') as rpgenes:
                data = rpgenes.read()
            with track.load('/tmp/ae456f0', 'sql') as t:
                data = t.read()
            with track.load('tracks/repeats.bed', readonly=True) as repeats:
                data = repeats.read()
            with track.load('http://example.com/genes.bed') as genes:
                data = genes.read()
    """
    # Check if URL #
    path = if_url_then_get_url(path)
    # Check not empty #
    check_file(path)
    # Guess the format #
    if not format: format = determine_format(path)
    # If sql, just make a track with the path #
    # Otherwise we need to convert the file #
    if format == 'sql':
        return Track(path, readonly)
    else:
        sql_path = temporary_path(".sql") or os.path.splitext(path)[0] + ".sql"
        convert(source=(path, format), destination=(sql_path, 'sql'))
        return Track(sql_path, readonly=readonly, orig_path=path, orig_format=format)

#---------------------------------------------------------------------------------#
def new(path, format=None):
    """Creates a new empty track in preparation for writing to it.

       :param path: is the path to track file to create.
       :type  path: string
       :param format: is an optional parameter specifying the format of the track to create when it cannot be guessed from the file extension.
       :type  format: string
       :returns: a Track instance

       ::

           import track
           with track.new('tmp/track.sql') as t:
               t.write('chr1', [(10, 20, 'Gene A', 0.0, 1)])
               t.set_chrmeta('hg19')
           with track.new('tracks/peaks.sql', 'sql') as t:
               t.fields = ['start', 'end', 'name', 'score']
               t.write('chr5', [(500, 1200, 'Peak1', 11.3)])
    """
    # Guess the format #
    if not format: format = os.path.splitext(path)[1][1:].lower()
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
def convert(source, destination, assembly=None):
    """Converts a track from one format to an other. The *source* file should have a different format from the *destination* file. If either the source or destination are missing a file extension, you can specify their formats using a tuple. See examples below.

       :param source: is the path to the original track to load.
       :type  source: string
       :param destination: is the path to the track to be created.
       :type  destination: string
       :param assembly: an optional GenRep compatible assembly name or id. Useful when the destination format needs to contain chromosome meta data and this is not available in the source file.
       :type  assembly: string

       :returns: the path to the track created (or a list of track paths in the case of multi-track files).

       ::

           import track
           track.convert('tracks/genes.bed', 'tracks/genes.sql')
           track.convert('tracks/genes.sql', 'tracks/genes.bigWig', assembly='hg19')
           track.convert(('tracks/no_extension', 'gff'), 'tracks/genes.sql')
           track.convert(('tmp/4afb0edf', 'bed'), ('tmp/converted', 'wig'))
    """
    # Parse the source parameter #
    if isinstance(source, tuple):
        source_path   = if_url_then_get_url(source[0])
        source_format = source[1]
    else:
        source_path   = if_url_then_get_url(source)
        source_format = determine_format(source_path)
    # Parse the destination parameter #
    if isinstance(destination, tuple):
        destination_path   = destination[0]
        destination_format = destination[1]
    else:
        destination_path   = destination
        destination_format = determine_format(destination_path)
    # Check it is not taken #
    check_path(destination_path)
    # Special cases #
    if destination_format == 'bigwig' and source_format != 'sql':
        source_path = convert((source_path, source_format), temporary_path('.sql'), assembly)
        source_format = 'sql'
    # Check it is not empty #
    check_file(source_path)
    # Check for compressed files #
    if is_gzip(source_path): source_format = gzip_inner_format(source_path)
    # Get a parser #
    parser = get_parser(source_path, source_format)
    # Get a serializer #
    serializer = get_serializer(destination_path, destination_format)
    # Tell the serializer about the assembly #
    if assembly: serializer.defineAssembly(assembly)
    # The serializer has a copy of the parser and vice-versa #
    serializer(parser)
    return parser(serializer)

################################################################################
class Track(object):
    """The track object itself is iterable and will yield the name of all chromosomes.
    ::

        import track
        with track.load('tracks/all_genes.sql') as t:
            for chrom in t: print chrom
            if 'chrY' in t: print 'Male'
            if len(t) != 23: print 'Aneuploidy'
    """

    def __init__(self, path, readonly=False, autosave=True, orig_path=None, orig_format=None):
        """The track package is designed to be accesed via the 'load()' and 'new()'
           functions in order to create Track objects.
           Usually, the constructor is not called directly."""
        # Passed attributes #
        self.path        = path
        self.readonly    = readonly
        self.autosave    = autosave
        self.orig_path   = orig_path
        self.orig_format = orig_format
        # Hidden attributes #
        self._modified = False
        self._fields   = []
        self._chrmeta  = JournaledDict()
        self._info     = JournaledDict()
        # Opening the database #
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = SuperRow
        # A list to hold all cursors #
        self.all_cursors = []
        # Make two cursors #
        self._cursor       = self.cursor()
        self._write_cursor = self.cursor()
        # Load some tables #
        self._chrmeta_read()
        self._info_read()

    def __enter__(self):
        """Called when entering the 'with' statement."""
        return self

    def __exit__(self, errtype, value, traceback):
        """Called when exiting the 'with' statement.
        Enables us to close the database properly, even when exceptions are raised."""
        self.close()

    def __iter__(self):
        """Called when evaluating ``for chrom in t: pass``."""
        return iter(self.chromosomes)

    def __contains__(self, key):
        """Called when evaluating ``"chr1" in t``."""
        return key in self.chromosomes

    def __len__(self):
        """Called when evaluating ``len(t)``."""
        return len(self.chromosomes)

    def __nonzero__(self):
        """Called when evaluating ``if t: pass``."""
        return True

    def __getitem__(self, key):
        """Called when evaluating ``t[0] or t['chr1']``."""
        if isinstance(key,int): return self.chromosomes[key]
        else: return self.read(key)

    #-----------------------------------------------------------------------------#
    @property
    def modified(self):
        """*modified* is a boolean value which indicates if the track has been changed since it was opened. This value is set to False when you load a track and is set to True as soon, as you ``write``, ``rename`` or ``remove``. Changing the ``info`` or ``chrmeta`` attributes will also set this value to True."""
        if self._modified or self.info.modified or self.chrmeta.modified: return True
        return False

    @property
    def fields(self):
        """*fields* is a list the value types that each feature in the track will contain. For instance:

               ``['start', 'end', 'name', 'score', 'strand']``

           Setting this attribute will influence the behaviour of all future read() and write() calls."""
        # Checks the user set self._fields attribute. If it is empty,
        # it gets the field names of the first chromosome table
        # it finds.
        if self._fields: return self._fields
        elif self.chromosomes: return self._get_fields_of_table(self.chromosomes[0])
        else: return []

    @fields.setter
    def fields(self, value):
        """Set the fields globally for the track. This value is then used by read() and write() to get the fields in the right order."""
        self._fields = value

    @property
    def tables(self):
        """Returns the complete list of SQL tables."""
        self._cursor.execute("select name from sqlite_master where type='table'")
        return [x[0].encode('ascii') for x in self._cursor.fetchall()]

    @property
    def chromosomes(self):
        """*chromosomes* is a list of all available chromosome. For instance:

               ``['chr1, 'chr2', 'chr3', 'chr4', 'chr5', 'chrC', 'chrM']``

           You cannot set this attribute. To add new chromosomes, just ``write()`` to them."""
        # Filters the list of SQL tables to retrieve the list of chromosomes.
        chroms = [x for x in self.tables if x not in special_tables and not x.endswith('_idx')]
        chroms.sort(key=natural_sort)
        return chroms

    def _get_fields_of_table(self, chrom):
        """Returns the list of fields for a particular table by querying the SQL for the complete list of column names"""
        # Check the table exists #
        if not chrom in self.tables: return []
        # A pragma statement will implicitly issue a commit, don't use #
        self._cursor.execute("SELECT * from '%s' LIMIT 1" % chrom)
        fields = [x[0] for x in self._cursor.description]
        self._cursor.fetchall()
        return fields

    #-----------------------------------------------------------------------------#
    def cursor(self):
        """*cursor* will create a new sqlite3 cursor object connected to the track database. You can use this attribute to make your own SQL queries and fetch the results. More information is available on the `sqlite3 documentation pages <http://docs.python.org/library/sqlite3.html>`_.

        :returns: A new sqlite3 cursor object

        ::

            import track
            with track.load('tracks/rp_genes.sql') as rpgenes:
                cursor = rpgenes.cursor()
                cursor.execute("select name from sqlite_master where type='table'")
                results = cursor.fetchall()
        """
        new_cursor = self._connection.cursor()
        self.all_cursors.append(new_cursor)
        return new_cursor

    #-----------------------------------------------------------------------------#
    def save(self):
        """Stores the changes that were applied to the track on the disk. If the track was loaded from a text file such as 'bed', the file is rewritten with the changes included. If the track was loaded as an SQL file, the changes are committed to the database. Calling ``rollback`` will revert all changes to the track since the last call to ``save()``. By default, when the track is closed, all changes are saved.

        :returns: None

        ::

           import track
           with track.load('tracks/rp_genes.bed') as t:
               t.remove('chr19_gl000209_random')
               t.save()
        """
        if self._info.modified:    self._info_write()
        if self._chrmeta.modified: self._chrmeta_write()
        self._make_missing_tables()
        self._make_missing_indexes()
        self._connection.commit()

    def _make_missing_indexes(self):
        """For every chromosomes present in the track, will create an index on the following fields if they exist:
                * start, end --> chr1_range_idx
                * score      --> chr1_score_idx
                * name       --> chr1_name_idx
        """
        if self.readonly: return
        try:
            for ch in self:
                if 'start' in self._get_fields_of_table(ch):
                    self._cursor.execute("CREATE INDEX if not exists '" + ch + "_range_idx' on '" + ch + "' (start,end)")
                if 'score' in self._get_fields_of_table(ch):
                    self._cursor.execute("CREATE INDEX if not exists '" + ch + "_score_idx' on '" + ch + "' (score)")
                if 'name' in self._get_fields_of_table(ch):
                    self._cursor.execute("CREATE INDEX if not exists '" + ch + "_name_idx' on '" +  ch + "' (name)")
        except sqlite3.OperationalError as err:
            message = "The index creation on the track '%s' failed with the following error: %s"
            raise Exception(message % (self.path, err))

    def _make_missing_tables(self):
        """Makes sure every chromsome referenced in the chrNames table exists as a table in the database. Will create empty tables."""
        fields = self.fields or minimum_fields
        fields = ','.join(['"' + f + '"' + ' ' + sql_field_types.get(f, 'text') for f in fields])
        for chrom_name in sorted(self.chrmeta, key=natural_sort):
            self._cursor.execute('CREATE table if not exists "' + chrom_name + '" (' + fields + ')')

    #-----------------------------------------------------------------------------#
    def rollback(self):
        """Reverts all changes to the track since the last call to ``save()``.

        :returns: None

        ::

           import track
           with track.load('tracks/rp_genes.bed') as t:
               t.remove('chr19_gl000209_random')
               t.export('tmp/clean.bed')
               t.rollback()
        """
        self._connection.rollback()

    #-----------------------------------------------------------------------------#
    def vacuum(self):
        """Rebuilds the database making it shrink in file size. This method is useful when, after having executed many inserts, updates, and deletes, the SQLite file is fragmented and full of empty space.

        :returns: None

        ::

           import track
           with track.load('tracks/rp_genes.bed') as t:
               t.remove('chr19_gl000209_random')
               t.vaccum()
        """
        self._cursor.execute("VACUUM")

    #-----------------------------------------------------------------------------#
    def close(self):
        """Closes the current track. This method is useful when for some special reason you are not using the 'with ... as' form for loading tracks.

        :returns: None

        ::

            import track
            t = track.load('tracks/rp_genes.bed')
            t.remove('chr19_gl000209_random')
            t.close()
        """
        # Commit changes to the database #
        if self.modified and self.autosave: self.save()
        # Close all cursors #
        for cur in self.all_cursors: cur.close()
        # Close the connection #
        self._connection.close()
        # If the original file was not an sql #
        if not self.readonly and self.orig_path:
            # Rewrite the file #
            if os.path.exists(self.orig_path): os.remove(self.orig_path)
            convert(self.path, (self.orig_path, self.orig_format))
            # Remove the temporary SQL #
            os.remove(self.path)

    #-----------------------------------------------------------------------------#
    def export(self, path, format=None):
        """Exports the current track to a given format. A new file is created at the specified path. The current track object is unchanged

        :param path: is the path to track file to create.
        :type  path: string
        :param format: is an optional parameter specifying the format of the track to create when it cannot be guessed from the file extension.
        :type  format: string
        :returns: None

        ::

            import track
            with track.load('tracks/rp_genes.bed') as t:
                t.remove('chr19_gl000209_random')
                t.export('tmp/clean.bed')
                t.rollback()
        """
        # Check it is not taken #
        check_path(path)
        # Guess format #
        if not format: format = determine_format(path)
        # Get a serializer #
        serializer = get_serializer(path, format)
        # Get a parser #
        parser = get_parser(self, 'sql')
        # Do it #
        return parser(serializer)

    #-----------------------------------------------------------------------------#
    def read(self, selection=None, fields=None, order='start,end'):
        """Reads data from the track.

        :param selection: A chromosome name, or a dictionary specifying a region, see below.
        :param fields: is an optional list of fields which will influence the length of the tuples returned and the way in which the information is returned. The default is to read every field available for the given chromosome. If the *track.fields* attribute is set, that will be used.
        :type  fields: list of strings
        :param order: is am optional sublist of *fields* which will influence the order in which the tuples are yielded. By default results are sorted by ``start`` and, secondly, by ``end``.
        :type  order: list of strings

        :returns: a generator object yielding rows. A row can be referenced like a tuple or like a dictionary.

        *selection* can be the name of a chromosome, in which case all the data on that chromosome will be returned.

        *selection* can be left empty, then the data from all chromosome is returned.

        *selection* can also be a dictionary specifying: regions, score intervals or strands. If you specify a region in which case only features contained in that region will be returned. But you can also input a tuple specifying a score interval in which case only features contained in those score boundaries will be returned. You can even specify a strand. The dictionary can contain one or several of these arguments. See code example for more details.

        Adding the parameter ``'inclusion':'strict'`` to a region dictionary will return only features exactly contained inside the interval instead of features simply included in the interval. To combine multiple selections you can specify a list including chromosome names and region dictionaries. As expected, if such is the case, the joined data from those selections will be returned with an added ``chr`` field in front since the results may span several chromosomes.

        ::

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
        """
        # Default values #
        where = None
        ##### SELECTION #####
        if not selection: selection = self.chromosomes
        # Case list of things #
        if isinstance(selection, (list, tuple)):
            return join_read_queries(self, selection, fields)
        # Case selection dictionary #
        elif isinstance(selection, dict):
            chrom = selection['chr']
            where = " WHERE " + make_cond_from_sel(selection)
        # Case chromosome name #
        elif isinstance(selection, basestring): chrom = selection
        # Other cases #
        else: raise TypeError, 'The following selection parameter: "' + selection + '" was not understood.'
        # Empty chromosome case #
        if chrom not in self.chromosomes: return ()
        ##### FIELDS #####
        if not fields and not self._fields: query_fields = "*"
        else:
            # Columns names in the table #
            available_fields = self._get_fields_of_table(chrom)
            # Fields attribute is set or not #
            query_fields = ','.join([f in available_fields and f or py_field_types[f]().__repr__() for f in fields and fields or self._fields])
        ##### QUERY #####
        sql_command = "SELECT " + query_fields + " from '" + chrom + "'"
        # Add the where case #
        if where: sql_command += where
        # Sorting results #
        if order: sql_command += ' order by ' + order
        # Make a new cursor #
        cursor = self.cursor()
        ##### ERROR CATCHING #####
        try:
            cursor.execute(sql_command)
        except sqlite3.OperationalError as err:
            message = "The command <%s%s%s> on the track '%s' failed with error:\n\n %s%s%s"
            message = message % (Color.cyn, sql_command, Color.end, self.path, Color.u_red, err, Color.end)
            raise Exception(message)
        # Make a feature stream #
        return FeatureStream(cursor)

    #-----------------------------------------------------------------------------#
    def write(self, chromosome, data, fields=None):
        """Writes data to a genomic file. Will write many feature at once into a given chromosome.

        :param chromosome: is the name of the chromosome on which one wants to write. For instance, if one is using the BED format this will become the first column, while if one is using the SQL format this will become the name of the table to be created.
        :type  chromosome: string
        :param data: must be an iterable object that yields tuples or rows of the correct length. As an example, the ``read`` function of this class produces such objects. *data* can have a *fields* attribute describing what the different elements of the tuple represent. *data* can also simply be a list of tuples.
        :type  data: an iteratable
        :param fields: is a parameter describing what the different elements in *data* represent. It is optional and is used only if *data* doesn't already have a ``fields`` attribute.
        :type  fields: list of strings

        :returns: None

        ::

            import track
            with track.load('tracks/example.sql') as t:
                t.write('chr1', [(10, 20, 'A', 0.0, 1), (40, 50, 'B', 0.0, -1)])
            with track.load('tracks/example.sql') as t:
                def example_generator():
                    for i in xrange(5):
                        yield (10, 20, 'X')
                t.write('chr2', example_generator(), fields=['start','end','name'])
            with track.load('tracks/new.sql') as t2:
                with track.load('tracks/orig.sql') as t1:
                    t1.write('chr1', t2.read('chr1'))
        """
        # Check track attributes #
        if self.readonly: return
        self._modified = True
        # Check what the data generator yields #
        if isinstance(data, FeatureStream) and data.kind == SuperRow: data.generator = imap(tuple,data)
        # Guess the fields we are getting #
        if fields:                           incoming_fields = fields
        elif hasattr(data, 'fields'):        incoming_fields = data.fields
        elif hasattr(data, 'description'):   incoming_fields = [x[0] for x in data.description]
        elif self._fields:                   incoming_fields = self._fields
        elif chromosome in self.chromosomes: incoming_fields = self._get_fields_of_table(chromosome)
        else:                                incoming_fields = default_fields
        # Current fields present in table #
        chrom_exists = chromosome in self.chromosomes
        current_fields = chrom_exists and self._get_fields_of_table(chromosome) or []
        # The fields we want to write #
        if self._fields: outgoing_fields = self._fields
        else:            outgoing_fields = incoming_fields
        # Make them sets #
        outgoing_set = set(outgoing_fields)
        incoming_set = set(incoming_fields)
        current_set  = set(current_fields)
        # Maybe we need to create the table #
        if not chrom_exists:
            fields = ','.join(['"' + field + '"' + ' ' + sql_field_types.get(field, 'text') for field in outgoing_fields])
            self._write_cursor.execute('CREATE table "' + chromosome + '" (' + fields + ')')
            current_fields = outgoing_fields
        # Or maybe we need to create new columns #
        else:
            for field in outgoing_set - current_set:
                self._write_cursor.execute('ALTER table "' + chromosome + '" ADD "' + field + '" ' + sql_field_types.get(field, 'text'))
        # Adjust size #
        if outgoing_set > incoming_set:
            outgoing_fields = incoming_fields
        if outgoing_set < incoming_set:
            indicies = tuple([incoming_fields.index(f) for f in outgoing_fields])
            data = pick_iterator_elements(data, indicies)
        # Protect names for SQL query #
        outgoing_fields = ['"' + f + '"' for f in outgoing_fields]
        question_marks = '(' + ','.join(['?' for x in xrange(len(outgoing_fields))]) + ')'
        sql_command = 'INSERT into "' + chromosome + '" (' + ','.join(outgoing_fields) + ') values ' + question_marks
        # Execute the insertion #
        try:
            self._write_cursor.executemany(sql_command, data)
        except (ValueError, sqlite3.OperationalError, sqlite3.ProgrammingError) as err:
            message1 = "The command <%s%s%s> on the track '%s' failed with error:\n %s%s%s"
            message1 = message1 % (Color.cyn, sql_command, Color.end, self.path, Color.u_red, err, Color.end)
            message2 = "\n * %sThe bindings%s: %s \n * %sYou gave%s: %s"
            message2 = message2 % (Color.b_ylw, Color.end, fields, Color.b_ylw, Color.end, data)
            message3 = "\n * %sFirst element%s: %s \n"
            message3 = message3 % (Color.b_ylw, Color.end, get_next_item(data))
            raise Exception(message1 + message2 + message3)

    #-----------------------------------------------------------------------------#
    def insert(self, chromosome, feature):
        """Inserts one feature into an existing chromosome.

        :param chromosome: is the name of the chromosome into which one wants to insert.
        :type  chromosome: string
        :param feature: must be a tuple of the right size to fit into the chromosome table.
        :type  feature: tuple

        :returns: None.

        ::

            import track
            with track.load('tracks/example.sql') as t:
                t.insert('chr1', (10, 20, 'A')
        """
        question_marks = '(' + ','.join(['?' for x in xrange(len(feature))]) + ')'
        self._write_cursor.execute('insert into "' + chromosome + '" values ' + question_marks, feature)

    #-----------------------------------------------------------------------------#
    def remove(self, chromosome):
        """Removes data from a given chromosome.

        :param chromosome: is the name of the chromosome that one wishes to delete or a list of chromosomes to delete.
        :type  chromosome: string

        :returns: None.

        ::

            import track
            with track.load('tracks/example.sql') as t:
                t.remove('chr1')
            with track.load('tracks/example.sql') as t:
                t.remove(['chr1', 'chr2', 'chr3'])
        """
        # Check track attributes #
        self._modified = True
        if self.readonly: return
        # Can be a list or a string #
        if isinstance(chromosome, list):
            for x in chromosome: self.remove(x)
        else:
            self._cursor.execute("DROP table '" + chromosome + "'")
            if chromosome in self.chrmeta: self.chrmeta.pop(chromosome)

    #-----------------------------------------------------------------------------#
    def rename(self, previous_name, new_name):
        """Renames a chromosome from *previous_name* to *new_name*

        :param previous_name: is the name of the chromosome that one wishes to rename.
        :type  previous_name: string
        :param new_name: is the name that that chromosome will now be referred by.
        :type  new_name: string

        :returns: None.

        ::

            import track
            with track.load('tracks/rp_genes.bed') as t:
                t.rename('chr4', 'chrIV')
        """
        # Check track attributes #
        self._modified = True
        if self.readonly: return
        # Check same name #
        if previous_name == new_name: return
        # Check previous exists #
        if previous_name not in self.chromosomes: raise Exception("The chromosome '" + previous_name + "' doesn't exist.")
        # Check new doesn't exist #
        if new_name in self.chromosomes:
            message = "The chromosome '%s' can't be renamed to '%s', as '%s' alredy exists."
            raise Exception(message % (previous_name, new_name, new_name))
        # Check different #
        if new_name == previous_name: return
        # SQL query #
        command = "ALTER TABLE '" + previous_name + "' RENAME TO '" + new_name + "'"
        try:
            self._cursor.execute(command)
        except sqlite3.OperationalError as err:
            message = "The command <%s%s%s> on the track '%s' failed with error:\n %s%s%s"
            message = message % (Color.cyn, command, Color.end, self.path, Color.u_red, err, Color.end)
            raise Exception(message)
        # Drop indexes #
        self._cursor.execute("drop index IF EXISTS '" + previous_name + "_range_idx'")
        self._cursor.execute("drop index IF EXISTS '" + previous_name + "_score_idx'")
        self._cursor.execute("drop index IF EXISTS '" + previous_name + "_name_idx'")
        # Rename the chrmeta #
        if previous_name in self.chrmeta:
            self.chrmeta[new_name] = self.chrmeta[previous_name]
            self.chrmeta.pop(previous_name)

    #-----------------------------------------------------------------------------#
    def search(self, query_dict, fields=None, chromosome=None, exact_match=False):
        """Searches for parameters inside your tracks. You can specify several parameters.
        :param selection: list of the fields you want to have in the result (to insure that all result will have the same number of columns)
        :param query_dict: A dictionary specifying keys and values to search for. See examples.
        :type  query_dict: dict
        :param chromosome: Optionally, the name of the chromosome on which one wants to search. If ``None``, the search is performed on all chromosomes and every feature contains a new field specifying its chromosome.
        :type  chromosome: string
        :param exact_match: By default, will find all entries which contain the query. If set to ``True``, will only find entries that exactly match the query.
        :type  exact_match: bool

        :returns: a generator object yielding rows. A row can be referenced like a tuple or like a dictionary.

        ::

           import track
           with track.load('tracks/rp_genes.bed') as t:
               results = t.search({'gene_id':3})
               results = t.search({'gene_id':3, 'gene_name':'YCCA3'}, 'chr1')
        """
        # A example final SQL string generated by this function is:
        # SELECT * from ("chrI","chrII","chrIII") WHERE gene_id like '%3%' AND gene_name like '%YCCA3%'
        conditions = []
        if fields is None :
            fields = self.fields
        # Generate condition #
        for k,v in query_dict.items():
            if exact_match: conditions.append(' %s = "%s" ' % (k,v))
            else:           conditions.append(' %s like "%%%s%%" ' % (k,v))
        where = ' WHERE ' + ' AND '.join(conditions)
        # Iterate on chromosomes #
        if chromosome: query_str = 'SELECT ' + ', '.join(fields) + ' from "%s"' % chromosome + where
        else:          query_str = ' UNION '.join(['SELECT "%s",' % chrom + ', '.join(fields) + ' from "%s"' % chrom + where for chrom in self])
        # Execute it #
        cursor = self.cursor()
        return cursor.execute(query_str)

    #-----------------------------------------------------------------------------#
    def count(self, selection=None):
        """Counts the number of features or entries in a given selection.

        :param selection: is the name of a chromosome, a list of chromosomes, a particular span or a list of spans. In other words, a value similar to the *selection* parameter of the *read* method. If left empty, will count every feature in a track

        :returns: an integer.

        ::

            import track
            with track.load('tracks/example.sql') as t:
                num = t.count('chr1')
                num = t.count(['chr1','chr2','chr3'])
                num = t.count({'chr':'chr1', 'start':10000, 'end':15000})
        """
        # Default selection #
        if not selection:
            selection = self.chromosomes
        # Case several chromosome #
        if isinstance(selection, list) or isinstance(selection, tuple):
            return sum([self.count(s) for s in selection])
        # Case chromosome name #
        elif isinstance(selection, basestring):
            if selection not in self.chromosomes: return 0
            sql_request = "select COUNT(*) from '" + selection + "'"
        # Case span dictionary #
        elif isinstance(selection, dict):
            chrom = selection['chr']
            if chrom not in self.chromosomes: return 0
            sql_request = "select COUNT(*) from '" + chrom + "' where " + make_cond_from_sel(selection)
        # Other cases #
        else: raise TypeError, 'The following selection parameter: "' + selection + '" was not understood'
        # Return the results #
        cursor = self.cursor()
        return cursor.execute(sql_request).fetchone()[0]

    #-----------------------------------------------------------------------------#
    def ucsc_to_ensembl(self):
        """Converts all entries of a track from the UCSC standard to the Ensembl standard effectively adding one to every start position.

        :returns: None.

        ::

           import track
           with track.load('tracks/example.sql') as t:
               t.ucsc_to_ensembl()
        """
        for chrom in self.chromosomes: self._cursor.execute("update '" + chrom + "' set start=start+1")

    def ensembl_to_ucsc(self):
        """Converts all entries of a track from the Ensembl standard to the UCSC standard effectively subtracting one from every start position.

        :returns: None.

        ::

           import track
           with track.load('tracks/rp_genes.bed') as t:
               t.ensembl_to_ucsc()
        """
        for chrom in self.chromosomes: self._cursor.execute("update '" + chrom + "' set start=start-1")

    #-----------------------------------------------------------------------------#
    def get_score_vector(self, chromosome):
        """Returns an iterable with as many elements as there are base pairs in the chromosomes specified by the *chromosome* parameter. Every element of the iterable is a float indicating the score at that position. If the track has no score associated, ones are inserted where features are present.

        :param chromosome: is the name of the chromosome on which one wants to create a score vector from.
        :type  chromosome: string

        :returns: an iterable yielding floats.

        ::

            import track
            with track.new('tmp/track.sql') as t:
                scores = t.get_score_vector('chr1')
        """
        # Conditions #
        if 'score' not in self.fields:
            def add_ones(X):
                for x in X: yield x + (1.0,)
            data = add_ones(self.read(chromosome, ['start','end']))
        else:
            data = self.read(chromosome, ['start','end','score'])
        # Initialization #
        last_end = 0
        x = (-1,0)
        # Core loop #
        for x in data:
            for i in xrange(last_end, x[0]): yield 0.0
            for i in xrange(x[0],     x[1]): yield x[2]
            last_end = x[1]
        # End piece #
        if self.chrmeta.get(chromosome):
            for i in xrange(x[1], self.chrmeta[chromosome]['length']): yield 0.0

    #-----------------------------------------------------------------------------#
    def roman_to_integer(self, names=None):
        """Converts the name of all chromosomes from the roman numeral standard to the arabic numeral standard. For instance, 'chrI' will become 'chr1' while 'chrII' will become 'chr2', etc.

        :param names: an optional dictionary specifying how to translate particular cases. Example: ``{'chrM':'chrQ', '2micron':'chrR'}``
        :type  names: dict

        :returns: None.

        ::

            import track
            with track.new('tmp/track.sql') as t:
                scores = t.roman_to_integer()
        """
        names = names or {'chrM':'chrQ', '2micron':'chrR'}
        def convert(chrom):
            if chrom in names: return names[chrom]
            match = re.search('([a-zA-Z]*?)([IVX]+)$', chrom)
            if match: return match.group(1) + str(roman_to_int(match.group(2)))
            else: return chrom
        for chrom in self: self.rename(chrom, convert(chrom))

    def integer_to_roman(self, names=None):
        """Converts the name of all chromosomes from the arabic numeral standard to the roman numeral standard. For instance, 'chr1' will become 'chrI' while 'chr2' will become 'chrII', etc.

        :param names: an optional dictionary specifying how to translate particular cases. Example: ``{'chrQ':'chrM', 'chrR':'2micron'}``
        :type  names: dict

        :returns: None.

        ::

            import track
            with track.new('tmp/track.sql') as t:
                scores = t.roman_to_integer()
        """
        names = names or {'chrQ':'chrM', 'chrR':'2micron'}
        def convert(chrom):
            if chrom in names: return names[chrom]
            match = re.search('([a-zA-Z]*)([0-9]+)$', chrom)
            if match: return match.group(1) + int_to_roman(int(match.group(2)))
            else: return chrom
        for chrom in self: self.rename(chrom, convert(chrom))

    #--------------------------------------------------------------------------#
    @property
    def info(self):
        """*info* is a dictionary of meta data associated to the track (information like the source, etc). For instance:

              ``{'datatype': 'signal', 'source': 'SGD', 'orig_name': 'splice_sites.bed'}``
        """
        return self._info

    @info.setter
    def info(self, value):
        self._info.overwrite(value)

    def _info_read(self):
        """Populates the *self.info* attribute with information found in the 'attributes' table."""
        if not 'attributes' in self.tables: return
        # Make a dictionary directly from the table #
        query = self._cursor.execute('SELECT key, value from "attributes"')
        self.info = dict(query.fetchall())
        # Freshly loaded, so not modified #
        self.info.modified = False

    def _info_write(self):
        """Rewrites the 'attributes' table so that it reflects the contents of the *self.info* attribute."""
        if self.readonly: return
        self._cursor.execute('DROP table IF EXISTS "attributes"')
        if not self.info: return
        # Write every dictionary entry #
        self._cursor.execute('CREATE table "attributes" ("key" text, "value" text)')
        for k in sorted(self.info.keys(), key=natural_sort):
            self._cursor.execute('INSERT into "attributes" ("key","value") values (?,?)', (k, self.info[k]))

    @property
    def datatype(self):
        """Giving a datatype to your track is optional. The default datatype is ``None``. Other possible datatypes are ``features``, ``signal`` or ``relational``. Changing the datatype imposes some conditions on the entries that the track contains. This attribute is stored inside the *info* dictionary::

            import track
            with track.new('tmp/track.sql') as t:
                t.datatype = 'signal'

        """
        return self.info.get('datatype', None)

    @datatype.setter
    def datatype(self, value):
        if value not in ['features', 'signal', 'relational']:
            raise Exception("The datatype you are trying to use is invalid: '" + str(value) + "'.")
        self.info['datatype'] = value

    @property
    def name(self):
        """Giving a name to your track is optional. The default name is ``Unnamed``. This attribute is stored inside the *info* dictionary."""
        return self.info.get('name', os.path.basename(self.path))

    @name.setter
    def name(self, value):
        self.info['name'] = value

    #-----------------------------------------------------------------------------#
    @property
    def chrmeta(self):
        """*chrmeta* is an attribute containing extra chromosomal meta data such chromosome length information. *chrmeta* is a dictionary where each key is a chromosome names. For instance:

             ``{'chr1': {'length': 197195432}, 'chr2': {'length': 129993255}}``

        You would hence use it like this::

            import track
            with track.load('tmp/track.sql') as t:
                print t.chrmeta['chr1']['length']

        Of course, genomic formats such as ``bed`` cannot store this kind of meta data. Hence, when loading tracks in these text formats, this information is lost once the track is closed."""
        return self._chrmeta

    @chrmeta.setter
    def chrmeta(self, value):
        self._chrmeta.overwrite(value)

    def _chrmeta_read(self):
        """Populates the self.chrmeta attribute with information found in the 'chrNames' table."""
        # If the table doesn't exist, just use the names
        if not 'chrNames' in self.tables:
            dictionary = dict([(chrom, dict()) for chrom in self])
        else:
            # Columns are the chromosome attributes #
            # ['name', 'length']
            columns = self._get_fields_of_table("chrNames")
            # Rows are the chromosome names #
            # [{'name': 'chr1', 'length': 1000}, {'name': 'chr2', 'length': 2000}]
            query = self._cursor.execute('SELECT * from "chrNames"').fetchall()
            rows = [dict([(k,r[i]) for i, k in enumerate(columns)]) for r in query]
            # Make a pretty dictionary of dictionaries #
            # {'chr1': {'length': 1000}, 'chr2': {'length': 2000}}
            dictionary = dict([(r['name'], dict([(k, r[k]) for k in columns if k != 'name'])) for r in rows])
        # Freshly loaded, so not modified #
        self.chrmeta = dictionary
        self.chrmeta.modified = False

    def _chrmeta_write(self):
        """Rewrites the 'chrNames' table so that it reflects the contents of the self.chrmeta attribute."""
        if self.readonly: return
        self._cursor.execute('DROP table IF EXISTS "chrNames"')
        if not self.chrmeta: return
        # Rows are the chromosome names #
        # [{'name': 'chr1', 'length': 1000}, {'name': 'chr2', 'length': 2000}]
        rows = [dict([('name', chrom)] + [(k,v) for k,v in self.chrmeta[chrom].items()]) for chrom in self.chrmeta]
        self._cursor.execute('CREATE table "chrNames" ("name" text, "length" integer)')
        for r in sorted(rows, key=lambda x: natural_sort(x['name'])):
            question_marks = '(' + ','.join(['?' for x in r.keys()]) + ')'
            column_names   = '(' + ','.join(['"' + k + '"' for k in r.keys()]) + ')'
            cell_values    = tuple(r.values())
            self._cursor.execute('INSERT into "chrNames" ' + column_names + ' values ' + question_marks, cell_values)

    def load_chr_file(self, path):
        """Set the *chrmeta* attribute of the track by loading a chromosome file. The chromosome file is structured as tab-separated text file containing two columns: the first specifies a chromosomes name and the second its length as an integer.

        :param path: is the file path to the chromosome file to load.
        :type  path: string

        :returns: None.
        """
        self.chrmeta = parse_chr_file(path)

    def export_chr_file(self, path):
        """Output the information contained in the *chrmeta* attribute into a plain text file. The chromosome file is structured as tab-separated text file containing two columns: the first specifies a chromosomes name and the second its length as an integer

        :param path: is the file path to the chromosome file to create.
        :type  path: string

        :returns: None.
        """
        serialize_chr_file(self.chrmeta, path)

    @property
    def assembly(self):
        """Giving an assembly to your track is optional. However, if you set this variable for your track, you should input with a GenRep compatible assembly name or id. Doing so, will download the relevant information from GenRep, set the *chrmeta* attribute and rename all the chromosome to their canonical names if a correspondence is found. You can also call ``guess_assembly()``. This attribute is also stored inside the *info* dictionary.

        ::

            import track
            track.convert('tracks/genes.bed', 'tracks/genes.sql')
            with track.load('tracks/genes.sql') as t:
                t.assembly = 'hg19'
        """
        return self.info.get('assembly', 'Unnamed')

    @assembly.setter
    def assembly(self, value):
        # Get the assembly #
        assembly = Assembly(value)
        # Check that it is valid #
        if not assembly.name: return
        # Check if the tables need renaming or deleting #
        for orig_name in self.chromosomes:
            cannonical_name = assembly.guess_chromosome_name(orig_name)
            if cannonical_name: self.rename(orig_name, cannonical_name)
            else: self.remove(orig_name)
        # Add the chrmeta #
        self.chrmeta = assembly.chrmeta
        # Add the attribute #
        self.info['assembly'] = assembly.name

################################################################################
class FeatureStream(object):
    """Contains an iterator yielding features and an extra
       fields attribute.

       @param data: the iterator (or cursor) itself.
       @param fields: the list of fields
    """

    def __init__(self, generator, fields=None, kind=None):
        # The generator itself #
        self.generator = generator
        # The type of elements yielded #
        if not kind and hasattr(generator, 'connection'): kind = generator.connection.row_factory or tuple
        self.kind = kind
        # The description of the elements inside #
        if not fields and hasattr(generator, 'description'): fields = [x[0] for x in generator.description]
        self.fields = fields

    def __repr__(self): return "FeatureStream containing %s" % self.generator

    def __iter__(self): return self.generator

    def next(self): return self.generator.next()

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
