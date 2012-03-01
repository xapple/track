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

Be sure to read the chapter about :ref:`convention` to understand the result.

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
